#!/usr/bin/env python
# coding: utf-8

# This is based on [this previous kernel of mine](https://www.kaggle.com/ceshine/pytorch-bert-baseline-public-score-0-54). In the previous kernel only the context vectors corresponding to the first token of each name candidate were extracted and fed to the fully connected layer.
# 
# Here we use [`SelfAttentiveSpanExtractor` from AllenNLP](https://github.com/allenai/allennlp/blob/580dc8b0e2c6491d4d75b54c3b15b34b462e0c67/allennlp/modules/span_extractors/self_attentive_span_extractor.py) to utilize the full span (and their context vectors) of each name candidate. (Note that the target pronouns are always tokenized into a single token, so we only need to extract one context vector per pronoun.)
# 
# I have yet to observe any significant gains in accuracies from using the full spans, though (it's worse most of the time, in fact). Hyper-parameters even seem to become tricker to tune.

# In[ ]:


get_ipython().system('conda remove -y greenlet')
get_ipython().system('pip install pytorch-pretrained-bert')
get_ipython().system('pip install allennlp')
get_ipython().system('pip install https://github.com/ceshine/pytorch_helper_bot/archive/master.zip')


# In[ ]:


get_ipython().system('wget https://github.com/google-research-datasets/gap-coreference/raw/master/gap-development.tsv -q')
get_ipython().system('wget https://github.com/google-research-datasets/gap-coreference/raw/master/gap-test.tsv -q')
get_ipython().system('wget https://github.com/google-research-datasets/gap-coreference/raw/master/gap-validation.tsv -q')


# "pytorch_helper_bot" is a thin abstraction of some common PyTorch training routines. It can easily be replaced, so you can mostly ignore it and focus on the preprocessing and model definition instead.

# In[ ]:


import os

# This variable is used by helperbot to make the training deterministic
os.environ["SEED"] = "19543"

import logging
from pathlib import Path

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from pytorch_pretrained_bert import BertTokenizer
from pytorch_pretrained_bert.modeling import BertModel
from allennlp.modules.span_extractors import SelfAttentiveSpanExtractor

from helperbot import BaseBot, TriangularLR


# In[ ]:


BERT_MODEL = 'bert-base-uncased'
CASED = False


# In[ ]:


class Head(nn.Module):
    """The MLP submodule"""
    def __init__(self, bert_hidden_size: int):
        super().__init__()
        self.bert_hidden_size = bert_hidden_size
        self.span_extractor = SelfAttentiveSpanExtractor(bert_hidden_size)
        self.fc = nn.Sequential(
            nn.BatchNorm1d(bert_hidden_size * 3),
            nn.Dropout(0.1),             
            nn.Linear(bert_hidden_size * 3, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Dropout(0.5),          
            nn.Linear(64, 3)
        )
        for i, module in enumerate(self.fc):
            if isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d)):
                nn.init.constant_(module.weight, 1)
                nn.init.constant_(module.bias, 0)
                print("Initing batchnorm")
            elif isinstance(module, nn.Linear):
                if getattr(module, "weight_v", None) is not None:
                    nn.init.uniform_(module.weight_g, 0, 1)
                    nn.init.kaiming_normal_(module.weight_v)
                    print("Initing linear with weight normalization")
                    assert model[i].weight_g is not None
                else:
                    nn.init.kaiming_normal_(module.weight)
                    print("Initing linear")
                nn.init.constant_(module.bias, 0)
                
    def forward(self, bert_outputs, offsets):
        assert bert_outputs.size(2) == self.bert_hidden_size
        spans_contexts = self.span_extractor(
            bert_outputs, 
            offsets[:, :4].reshape(-1, 2, 2)
        ).reshape(-1, 2 * self.bert_hidden_size)
        return self.fc(torch.cat([
            spans_contexts,
            torch.gather(
                bert_outputs, 1,
                offsets[:, 4:].unsqueeze(2).expand(-1, -1, self.bert_hidden_size)
            ).squeeze(1)
        ], dim=1))


# In[ ]:


def tokenize(row, tokenizer):
    break_points = sorted(
        [
            ("A", row["A-offset"], row["A"]),
            ("B", row["B-offset"], row["B"]),
            ("P", row["Pronoun-offset"], row["Pronoun"]),
        ], key=lambda x: x[0]
    )
    tokens, spans, current_pos = [], {}, 0
    for name, offset, text in break_points:
        tokens.extend(tokenizer.tokenize(row["Text"][current_pos:offset]))
        # Make sure we do not get it wrong
        assert row["Text"][offset:offset+len(text)] == text
        # Tokenize the target
        tmp_tokens = tokenizer.tokenize(row["Text"][offset:offset+len(text)])
        spans[name] = [len(tokens), len(tokens) + len(tmp_tokens) - 1] # inclusive
        tokens.extend(tmp_tokens)
        current_pos = offset + len(text)
    tokens.extend(tokenizer.tokenize(row["Text"][current_pos:offset]))
    assert spans["P"][0] == spans["P"][1]
    return tokens, (spans["A"] + spans["B"] + [spans["P"][0]])


class GAPDataset(Dataset):
    """Custom GAP Dataset class"""
    def __init__(self, df, tokenizer, labeled=True):
        self.labeled = labeled
        if labeled:
            tmp = df[["A-coref", "B-coref"]].copy()
            tmp["target"] = 0
            tmp.loc[tmp['B-coref']  == 1, "target"] = 1
            tmp.loc[~(tmp['A-coref'] | tmp['B-coref']), "target"] = 2
            self.y = tmp.target.values.astype("uint8")
        
        self.offsets, self.tokens = [], []
        for _, row in df.iterrows():
            tokens, offsets = tokenize(row, tokenizer)
            self.offsets.append(offsets)
            self.tokens.append(tokenizer.convert_tokens_to_ids(
                ["[CLS]"] + tokens + ["[SEP]"]))
        
    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, idx):
        if self.labeled:
            return self.tokens[idx], self.offsets[idx], self.y[idx]
        return self.tokens[idx], self.offsets[idx], None

    
def collate_examples(batch, truncate_len=490):
    """Batch preparation.
    
    1. Pad the sequences
    2. Transform the target.
    """    
    transposed = list(zip(*batch))
    max_len = min(
        max((len(x) for x in transposed[0])),
        truncate_len
    )
    tokens = np.zeros((len(batch), max_len), dtype=np.int64)
    for i, row in enumerate(transposed[0]):
        row = np.array(row[:truncate_len])
        tokens[i, :len(row)] = row
    token_tensor = torch.from_numpy(tokens)
    # Offsets
    offsets = torch.stack([
        torch.LongTensor(x) for x in transposed[1]
    ], dim=0) + 1 # Account for the [CLS] token
    # Labels
    if len(transposed) == 2:
        return token_tensor, offsets, None
    labels = torch.LongTensor(transposed[2])
    return token_tensor, offsets, labels

    
class GAPModel(nn.Module):
    """The main model."""
    def __init__(self, bert_model: str, device: torch.device):
        super().__init__()
        self.device = device
        if bert_model in ("bert-base-uncased", "bert-base-cased"):
            self.bert_hidden_size = 768
        elif bert_model in ("bert-large-uncased", "bert-large-cased"):
            self.bert_hidden_size = 1024
        else:
            raise ValueError("Unsupported BERT model.")
        self.bert = BertModel.from_pretrained(bert_model).to(device)
        self.head = Head(self.bert_hidden_size).to(device)
    
    def forward(self, token_tensor, offsets):
        token_tensor = token_tensor.to(self.device)
        bert_outputs, _ =  self.bert(
            token_tensor, attention_mask=(token_tensor > 0).long(), 
            token_type_ids=None, output_all_encoded_layers=False)
        head_outputs = self.head(bert_outputs, offsets.to(self.device))
        return head_outputs            


# Adapted from fast.ai library
def children(m):
    return m if isinstance(m, (list, tuple)) else list(m.children())


def set_trainable_attr(m, b):
    m.trainable = b
    for p in m.parameters():
        p.requires_grad = b


def apply_leaf(m, f):
    c = children(m)
    if isinstance(m, nn.Module):
        f(m)
    if len(c) > 0:
        for l in c:
            apply_leaf(l, f)

            
def set_trainable(l, b):
    apply_leaf(l, lambda m: set_trainable_attr(m, b))
    
    
class GAPBot(BaseBot):
    def __init__(self, model, train_loader, val_loader, *, optimizer, clip_grad=0,
        avg_window=100, log_dir="./cache/logs/", log_level=logging.INFO,
        checkpoint_dir="./cache/model_cache/", batch_idx=0, echo=False,
        device="cuda:0", use_tensorboard=False):
        super().__init__(
            model, train_loader, val_loader, 
            optimizer=optimizer, clip_grad=clip_grad,
            log_dir=log_dir, checkpoint_dir=checkpoint_dir, 
            batch_idx=batch_idx, echo=echo,
            device=device, use_tensorboard=use_tensorboard
        )
        self.criterion = torch.nn.CrossEntropyLoss()
        self.loss_format = "%.4f"
        
    def extract_prediction(self, tensor):
        return tensor
    
    def snapshot(self):
        """Override the snapshot method because Kaggle kernel has limited local disk space."""
        loss = self.eval(self.val_loader)
        loss_str = self.loss_format % loss
        self.logger.info("Snapshot loss %s", loss_str)
        self.logger.tb_scalars(
            "losses", {"val": loss},  self.step)
        target_path = (
            self.checkpoint_dir / "best.pth")        
        if not self.best_performers or (self.best_performers[0][0] > loss):
            torch.save(self.model.state_dict(), target_path)
            self.best_performers = [(loss, target_path, self.step)]
        self.logger.info("Saving checkpoint %s...", target_path)
        assert Path(target_path).exists()
        return loss


# In[ ]:


df_train = pd.read_csv("gap-test.tsv", delimiter="\t")
df_val = pd.read_csv("gap-validation.tsv", delimiter="\t")
df_test = pd.read_csv("gap-development.tsv", delimiter="\t")
sample_sub = pd.read_csv("../input/sample_submission_stage_1.csv")
assert sample_sub.shape[0] == df_test.shape[0]


# In[ ]:


tokenizer = BertTokenizer.from_pretrained(
    BERT_MODEL,
    do_lower_case=CASED,
    never_split = ("[UNK]", "[SEP]", "[PAD]", "[CLS]", "[MASK]")
)


# In[ ]:


train_ds = GAPDataset(df_train, tokenizer)
val_ds = GAPDataset(df_val, tokenizer)
test_ds = GAPDataset(df_test, tokenizer)
train_loader = DataLoader(
    train_ds,
    collate_fn = collate_examples,
    batch_size=32,
    num_workers=4,
    pin_memory=True,
    shuffle=True,
    drop_last=True
)
val_loader = DataLoader(
    val_ds,
    collate_fn = collate_examples,
    batch_size=128,
    num_workers=2,
    pin_memory=True,
    shuffle=False
)
test_loader = DataLoader(
    test_ds,
    collate_fn = collate_examples,
    batch_size=128,
    num_workers=2,
    pin_memory=True,
    shuffle=False
)


# In[ ]:


model = GAPModel(BERT_MODEL, torch.device("cuda:0"))
# You can unfreeze the last layer of bert by calling set_trainable(model.bert.encoder.layer[23], True)
set_trainable(model.bert, False)
set_trainable(model.head, True)


# In[ ]:


optimizer = torch.optim.Adam(model.parameters(), lr=2e-3)
bot = GAPBot(
    model, train_loader, val_loader,
    optimizer=optimizer, echo=True,
    avg_window=25
)


# In[ ]:


steps_per_epoch = len(train_loader) 
n_steps = steps_per_epoch * 20
bot.train(
    n_steps,
    log_interval=steps_per_epoch // 4,
    snapshot_interval=steps_per_epoch,
    scheduler=TriangularLR(
        optimizer, 20, ratio=2, steps_per_cycle=n_steps)
)


# In[ ]:


# Load the best checkpoint
bot.load_model(bot.best_performers[0][1])


# In[ ]:


# Evaluate on the test dataset
bot.eval(test_loader)


# In[ ]:


# Extract predictions to the test dataset
preds = bot.predict(test_loader)


# In[ ]:


# Create submission file
df_sub = pd.DataFrame(torch.softmax(preds, -1).cpu().numpy().clip(1e-3, 1-1e-3), columns=["A", "B", "NEITHER"])
df_sub["ID"] = df_test.ID
df_sub.to_csv("cache/submission.csv", index=False)
df_sub.head()
