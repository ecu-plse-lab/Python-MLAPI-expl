#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().run_cell_magic('writefile', 'main.cpp', '#include <iostream>\n#include <fstream>\n#include <array>\n#include <algorithm>\n#include <vector>\n#include <random>\n#include <sstream>\n#include <cassert>\n\nusing namespace std;\ntypedef float feature_type;\ntypedef vector<vector<int>> grid;\nstruct box {\n    int xmin = 999, ymin = 999, xmax = -999, ymax = -999;\n    double width()  const {return xmin != 999 && xmax != -999 ? xmax - xmin : 0.0;}\n    double height() const {return ymin != 999 && ymax != -999 ? ymax - ymin : 0.0;}\n    double area() const {return width()*height();}\n    double perimeter() const {return 2*(width()+height());}\n    static box grid(const grid& g) {return box{0, 0, int(g.size()), int(g[0].size())};}\n    box reshape(int t) const {return box{xmin-t, ymin-t, xmax+t, ymax+t};}\n    bool has_box(box b) const {\n        return area() > 0 && b.area() > 0 && xmin <= b.xmin && xmax >= b.xmax && ymin <= b.ymin && ymax >= b.ymax;\n    }\n    bool has_intersection(box b) const {\n        return area() > 0 && b.area() > 0 && ymin < b.ymax && ymax > b.ymin && xmin < b.xmax && xmax > b.xmin;\n    }\n    double iou(box b) const {\n        double xmaxmin = max(xmin, b.xmin);\n        double ymaxmin = max(ymin, b.ymin);\n        double xminmax = min(xmax, b.xmax);\n        double yminmax = min(ymax, b.ymax);\n        \n        bool has_inter = has_intersection(b);\n        double inter_area = has_inter ? (xminmax - xmaxmin) * (yminmax - ymaxmin) : 0.0;\n        double whole_area = area() + b.area() - inter_area;\n        return inter_area / whole_area;\n    }\n};\nvector<string> split(istream& ss, char sep = \' \') {\n    vector<string> output;\n    string line;\n    for (;getline(ss, line, sep);) {\n        output.emplace_back(line);\n    }\n    return output;\n}\nvector<string> split(string input, char sep = \' \') {\n    istringstream ss(input);\n    return split(ss, sep);\n}\narray<int, 10> count(const grid& g, box b) {\n    array<int, 10> result;\n    result.fill(0);\n    for (auto x = b.xmin; x < b.xmax; ++x)\n        for (auto y = b.ymin; y < b.ymax; ++y)\n            ++result[g[x][y]];\n    return result;\n}\narray<int, 10> count(const grid& g) {\n    return count(g, box::grid(g));\n}\nbool has_vertical_symmetry(const grid& g, box b) {\n    for (int x = b.xmin; x<b.xmax; ++x)\n        for (int dy = 0; dy < (b.ymax-b.ymin)/2; ++dy) {\n            if (g[x][b.ymin+dy] != g[x][b.ymax-dy-1])\n                return false;\n        }\n    return true;\n}\nbool has_horizontal_symmetry(const grid& g, box b) {\n    for (int y = b.ymin; y < b.ymax; ++y)\n        for (int dx = 0; dx < (b.xmax-b.xmin)/2; ++dx) {\n            if (g[b.xmin+dx][y] != g[b.xmax-dx-1][y])\n                return false;\n        }\n    return true;\n}\nbool has_frame(const grid& g, box b, bool unique_frame = false) {\n    vector<int> cs;\n    int mx = int(g.size()), my = int(g[0].size());\n    int xmin_ = max(0, b.xmin), xmax_ = min(b.xmax, mx);\n    int ymin_ = max(0, b.ymin), ymax_ = min(b.ymax, my);\n    if (b.xmin == xmin_)\n        for (int y = ymin_; y < ymax_; ++y)\n            cs.emplace_back(g[b.xmin][y]);\n    if (b.xmax == xmax_)\n        for (int y = ymin_; y < ymax_; ++y)\n            cs.emplace_back(g[b.xmax-1][y]);\n    if (b.ymin == ymin_)\n        for (int x = xmin_; x < xmax_; ++x)\n            cs.emplace_back(g[x][b.ymin]);\n    if (b.ymax == ymax_)\n        for (int x = xmin_; x < xmax_; ++x)\n            cs.emplace_back(g[x][b.ymax-1]);\n    for (int i = 1; i < cs.size(); ++i)\n        if (cs[i] != cs[i-1])\n            return false;\n    if (unique_frame && !cs.empty())\n        for (int x = max(0, b.xmin+1); x < min(b.xmax-1, mx); ++x)\n            for (int y = max(0, b.ymin+1); y < min(b.ymax-1, my); ++y)\n                if (g[x][y] == cs[0])\n                    return false;\n    return true;\n}\nint cnt_strime(const grid& g, box b) {\n    int n = 0;\n    int mx = int(g.size()), my = int(g[0].size());\n    if (b.xmin >= b.xmax || b.ymin >= b.ymax)\n        return n;\n    int xmin_ = max(0, b.xmin), xmax_ = min(b.xmax, mx);\n    int ymin_ = max(0, b.ymin), ymax_ = min(b.ymax, my);\n    if (b.xmin == xmin_ && ymax_ - ymin_ > 1) {\n        ++n;\n        for (int y = ymin_+1; y < ymax_; ++y)\n            if (g[b.xmin][y-1] != g[b.xmin][y]) {\n                --n;\n                break;\n            }\n    }\n    if (b.xmax == xmax_ && ymax_ - ymin_ > 1) {\n        ++n;\n        for (int y = ymin_+1; y < ymax_; ++y)\n            if (g[b.xmax-1][y-1] != g[b.xmax-1][y]) {\n                --n;\n                break;\n            }\n    }\n    if (b.ymin == ymin_ && xmax_ - xmin_ > 1) {\n        ++n;\n        for (int x = xmin_+1; x < xmax_; ++x)\n            if (g[x-1][b.ymin] != g[x][b.ymin]) {\n                --n;\n                break;\n            }\n    }\n    if (b.ymax == ymax_ && xmax_ - xmin_ > 1) {\n        ++n;\n        for (int x = xmin_+1; x < xmax_; ++x)\n            if (g[x-1][b.ymax-1] != g[x][b.ymax-1]) {\n                --n;\n                break;\n            }\n    }\n    return n;\n}\nbool is_same_box(const grid& g, box l, box r) {\n    for (int dx = 0; dx < l.width(); ++dx)\n        for (int dy = 0; dy < l.height(); ++dy)\n            if (g[l.xmin+dx][l.ymin+dy] != g[r.xmin+dx][r.ymin+dy])\n                return false;\n    return true;\n}\nint cnt_same_boxes(const grid& g, box b) {\n    int n = 0;\n    int width = b.width();\n    int height = b.height();\n    for (int x = 0; x < g.size() - width; ++x)\n        for (int y = 0; y < g[0].size() - height; ++y) {\n            if (is_same_box(g, b, {x, y, width, height}))\n                ++n;\n        }\n    return n;\n}\narray<box, 10> get_boxes_of_colors(const grid& g) {\n    array<box, 10> boxes;\n    for (int x = 0; x < g.size(); ++x)\n        for (int y = 0; y < g[0].size(); ++y) {\n            int c = g[x][y];\n            boxes[c].xmin = min(boxes[c].xmin, x);\n            boxes[c].ymin = min(boxes[c].ymin, y);\n            boxes[c].xmax = max(boxes[c].xmax, x+1);\n            boxes[c].ymax = max(boxes[c].ymax, y+1);\n        }\n    return boxes;\n}\narray<box, 10> get_boxes_of_colors_inverse(const grid& g) {\n    array<box, 10> boxes;\n    for (int x = 0; x < g.size(); ++x)\n        for (int y = 0; y < g[0].size(); ++y) {\n            for (int c = 0; c < 10; ++c) if (c != g[x][y]) {\n                boxes[c].xmin = min(boxes[c].xmin, x);\n                boxes[c].ymin = min(boxes[c].ymin, y);\n                boxes[c].xmax = max(boxes[c].xmax, x+1);\n                boxes[c].ymax = max(boxes[c].ymax, y+1);\n            }\n        }\n    return boxes;\n}\nvoid boxes_features(vector<feature_type>& row, box l, box r) {\n//    row.emplace_back(l.area()/r.area());\n//    row.emplace_back(l.iou(r));\n    row.emplace_back(l.iou(r) > 0.99);\n}\nvector<int> get_colors(const grid& g, const array<box, 10>& boxes_of_colors, box bx) {\n    vector<int> colors;\n    auto cnt_colors = count(g, bx);\n    auto all_colors = count(g);\n    int used_color = -1;\n    int used_color2 = -1;\n    for (int  c = 9; c >= 0; --c) {\n        if (used_color != -1 && cnt_colors[c] > 0) {\n            used_color2 = c;\n            break;\n        }\n        if (used_color == -1 && cnt_colors[c] > 0) {\n            used_color = c;\n        }\n    }\n    int gr_percent = used_color;\n    int gr_area_not_black = used_color;\n    int gr_area = used_color;\n    int ls_area = used_color;\n    int gr_iou = used_color;\n    for (int c = 0; c < 10; ++c) {\n//        colors.emplace_back(c);\n        if (cnt_colors[gr_percent] / float(all_colors[gr_percent]) < cnt_colors[c] / float(all_colors[c]))\n            gr_percent = c;\n        if (boxes_of_colors[gr_area].area() < boxes_of_colors[c].area())\n            gr_area = c;\n        if (c != 0 && boxes_of_colors[gr_area_not_black].area() < boxes_of_colors[c].area())\n            gr_area_not_black = c;\n        if (boxes_of_colors[c].area() > 0 && boxes_of_colors[ls_area].area() > boxes_of_colors[c].area())\n            ls_area = c;\n        if (boxes_of_colors[gr_iou].iou(bx) < boxes_of_colors[c].iou(bx))\n            gr_iou = c;\n    }\n    int gr_area2 = gr_area == used_color ? used_color2 : used_color;\n    for (int c = 0; c < 10; ++c) {\n        if (c != gr_area && boxes_of_colors[gr_area2].area() < boxes_of_colors[c].area())\n            gr_area2 = c;\n    }\n    colors.emplace_back(gr_percent);        // 0\n    colors.emplace_back(gr_area_not_black); // 1\n    colors.emplace_back(gr_area);           // 2\n    colors.emplace_back(gr_area2);          // 3\n    colors.emplace_back(ls_area);           // 4\n    colors.emplace_back(gr_iou);            // 5\n    \n    return colors;\n}\nvector<feature_type> make_feature(const grid& g, const array<box, 10>& boxes_of_colors, const box bx) {\n    vector<feature_type> row;\n    row.emplace_back(bx.xmin);\n    row.emplace_back(bx.ymin);\n    row.emplace_back(bx.xmax);\n    row.emplace_back(bx.ymax);\n    \n    auto ibx = box::grid(g);\n    \n    int has_boxes = 0;\n    int in_boxes = 0;\n    auto boxes_of_colors_inverse = get_boxes_of_colors_inverse(g);\n    for (auto c : get_colors(g, boxes_of_colors, bx)) {\n        boxes_features(row, bx, boxes_of_colors[c]);\n        boxes_features(row, bx, boxes_of_colors_inverse[c]);\n        boxes_features(row, bx.reshape(1), boxes_of_colors[c]);\n        boxes_features(row, bx.reshape(1), boxes_of_colors_inverse[c]);\n    }\n    auto cnt_colors = count(g, bx);\n    int ucnt_colors = 0;\n    for (int c = 0; c < 10; ++c) {\n        ucnt_colors += cnt_colors[c] > 0;\n        has_boxes += bx.has_box(boxes_of_colors[c]);\n        in_boxes += boxes_of_colors[c].has_box(bx);\n    }\n    \n    boxes_features(row, bx, ibx);\n    bool has_frame_ = has_frame(g, bx);\n    bool has_frame_1 = has_frame(g, bx.reshape(1));\n//    bool has_frame_m1 = has_frame(g, bx.reshape(-1));\n    int cnt_trime_ = cnt_strime(g, bx);\n    row.emplace_back(cnt_same_boxes(g, bx));\n    row.emplace_back(has_frame_ ? cnt_same_boxes(g, bx) : 0);\n    row.emplace_back(cnt_trime_ == 0 ? cnt_same_boxes(g, bx) : 0);\n    row.emplace_back(has_vertical_symmetry(g, bx));\n    row.emplace_back(has_horizontal_symmetry(g, bx));\n\n    row.emplace_back(ucnt_colors);\n    row.emplace_back(has_boxes);\n    row.emplace_back(in_boxes);\n    row.emplace_back(has_frame(g, bx, true));\n    row.emplace_back(has_frame(g, bx.reshape(1), true));\n    row.emplace_back(has_frame_);\n    row.emplace_back(has_frame_1);\n//    row.emplace_back(has_frame_m1);\n    row.emplace_back(has_frame_1 || has_frame_);\n    row.emplace_back(has_frame_1 && has_frame_);\n    row.emplace_back(has_frame_1 == has_frame_);\n    row.emplace_back(bx.width());\n    row.emplace_back(bx.height());\n    row.emplace_back(bx.area());\n    row.emplace_back(cnt_trime_);\n    row.emplace_back(cnt_strime(g, bx.reshape(1)));\n    row.emplace_back(cnt_strime(g, bx.reshape(-1)));\n    \n//    row.emplace_back(perimeter);\n    return row;\n}\nstring get_columns() {\n    stringstream ss;\n    ss << "xmin" << "\\t";\n    ss << "ymin" << "\\t";\n    ss << "xmax" << "\\t";\n    ss << "ymax" << "\\t";\n    for (int i = 0; i < 7; ++i) {\n        for (int j = 0; j < 1 + 3*(i < 6); ++j) {\n//            ss << "[" << i << j << "] div_areas" << "\\t";\n//            ss << "[" << i << j << "] iou" << "\\t";\n            ss << "[" << i << j << "] iou_1" << "\\t";\n        }\n    }\n    ss << "cnt_same_boxes" << "\\t";\n    ss << "cnt_same_boxes_w_fr" << "\\t";\n    ss << "cnt_same_boxes_wo_tr" << "\\t";\n    ss << "has_vertical_symmetry" << "\\t";\n    ss << "has_horizontal_symmetry" << "\\t";\n    \n    ss << "ucnt_colors" << "\\t";\n    \n    ss << "has_boxes" << "\\t";\n    ss << "in_boxes" << "\\t";\n    ss << "has_uframe" << "\\t";\n    ss << "has_uframe_1" << "\\t";\n    ss << "has_frame" << "\\t";\n    ss << "has_frame_1" << "\\t";\n//    ss << "has_frame_1m" << "\\t";\n    ss << "has_frame_or" << "\\t";\n    ss << "has_frame_and" << "\\t";\n    ss << "has_frame_eq" << "\\t";\n    ss << "width" << "\\t";\n    ss << "height" << "\\t";\n    ss << "area" << "\\t";\n    ss << "cnt_strim" << "\\t";\n    ss << "cnt_strim_1" << "\\t";\n    ss << "cnt_strim_m1";\n//    ss << "perimeter";\n    return ss.str();\n}\nvoid make_features(const grid& g, ostream& out) {\n    auto boxes_of_colors = get_boxes_of_colors(g);\n    int n = 0;\n    box l = box::grid(g);\n    for (int xmin = 0; xmin < g.size(); ++xmin)\n        for (int ymin = 0; ymin < g[0].size(); ++ymin)\n            for (int xmax = xmin+1; xmax < g.size()+1; ++xmax)\n                for (int ymax = ymin+1; ymax < g[0].size()+1; ++ymax) {\n                    box r = {xmin, ymin, xmax, ymax};\n                    if (r.area() == l.area()) // || r.area() == 1) || (!has_frame(g, r) && !has_frame(g, r.reshape(1)))\n                        continue;\n                    auto row = make_feature(g, boxes_of_colors, r);\n                    out.write((char*)&row[0], row.size() * sizeof(row[0]));\n                    n += 1;\n                }\n    cout << "rows: " << n << endl;\n}\ninline bool exists(const std::string& name) {\n    ifstream f(name.c_str());\n    return f.good();\n}\nint main() {\n    string dir = "jupyter/arc/";\n    if (!exists(dir+"ex.txt"))\n        dir = "./";\n    vector<grid> inputs;\n    ifstream fin(dir + "ex.txt");\n    ofstream fout(dir + "features.bin", ios::out | ios::binary);\n    ofstream fcolumns(dir + "features.tsv");\n    fcolumns << get_columns();\n    for (auto input: split(fin, \' \')) {\n        vector<vector<int>> g;\n        for (auto line : split(input, \'|\')) {\n            vector<int> row;\n            for (char& c : line)\n                row.emplace_back(c-\'0\');\n            g.emplace_back(row);\n        }\n        inputs.emplace_back(g);\n    }\n    cout << "inputs: " << inputs.size() << endl;\n    auto features = make_feature({{1}}, get_boxes_of_colors({{1}}),{0, 0, 1, 1});\n    cout << "features: " << features.size() << endl;\n    cout << "columns: " << split(get_columns(), \'\\t\').size() << endl;\n    assert(features.size() == split(get_columns(), \'\\t\').size());\n    for (auto input : inputs) {\n        cout << "shape: " << input.size() << "x" << input[0].size() << endl;\n        make_features(input, fout);\n    }\n    return 0;\n}')


# In[ ]:


get_ipython().system('g++ -pthread -lpthread -O3 -std=c++17 -o main main.cpp')
get_ipython().system('./main')


# In[ ]:


from sklearn.tree import *
from sklearn import tree
from sklearn.ensemble import BaggingClassifier
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib
def plot_objects(objects, titles=None):
    if titles is None:
        titles = np.full(len(objects), '')
    cmap = matplotlib.colors.ListedColormap(['#000000', '#0074D9','#FF4136','#2ECC40','#FFDC00',
     '#AAAAAA', '#F012BE', '#FF851B', '#7FDBFF', '#870C25'])
    norm = matplotlib.colors.Normalize(vmin=0, vmax=9)
    fig, axs = plt.subplots(1, len(objects), figsize=(30,3), gridspec_kw = {'wspace':0.02, 'hspace':0.02}, squeeze=False)

    for i, (obj, title) in enumerate(zip(objects, titles)):
        obj = np.array(obj)
        axs[0,i].grid(True,which='both',color='lightgrey', linewidth=0.5)  
#         axs[i].axis('off')
        shape = ' '.join(map(str, obj.shape))
        axs[0,i].set_title(f"{title} {shape}")
        axs[0,i].set_yticks([x-0.5 for x in range(1+len(obj))])
        axs[0,i].set_xticks([x-0.5 for x in range(1+len(obj[0]))])
        axs[0,i].set_yticklabels([])     
        axs[0,i].set_xticklabels([])
        axs[0,i].imshow(obj, cmap=cmap, norm=norm)
    plt.show()
    
def plot_task(task):
    objects = []
    titles = []
    for key in ['train', 'test']:
        for obj in task[key]:
            objects.append(obj['input'])
            titles.append(f'{key} IN')
            if 'output' in obj:
                objects.append(obj['output'])
                titles.append(f'{key} OUT')
    plot_objects(objects, titles)


# In[ ]:


from skimage.measure import label, regionprops
from pathlib import Path

import numpy as np
import pandas as pd
from numpy import array
import os,json
from collections import defaultdict, Counter

kaggle_dir = '/kaggle/input/abstraction-and-reasoning-challenge/'
data_path = Path(kaggle_dir) if os.path.exists(kaggle_dir) else Path('./')
test_path = data_path / 'test'

def flattener(pred):
    str_pred = str([row for row in pred])
    str_pred = str_pred.replace(', ', '')
    str_pred = str_pred.replace('[[', '|')
    str_pred = str_pred.replace('][', '|')
    str_pred = str_pred.replace(']]', '|')
    return str_pred

def find_sub(matrix, sub):
    positions = []
    for x in range(matrix.shape[0]-sub.shape[0]+1):
        for y in range(matrix.shape[1]-sub.shape[1]+1):
            if np.equal(matrix[x:x+sub.shape[0], y:y+sub.shape[1]], sub).all():
                positions.append((x,y,x+sub.shape[0],y+sub.shape[1]))
    return positions

def check_subitem(task):
    for key in ['train', 'test']:
        for obj in task[key]:
            if 'output' in obj:
                x = np.array(obj['input'])
                y = np.array(obj['output'])
                if len(find_sub(x, y)) == 0:
                    return False
    return True 

def get_objects(task, has_train=True, has_test=False):
    xs, ys = [], []
    names = []
    if has_train:
        names.append('train')
    if has_test:
        names.append('test')
    for key in names:
        for obj in task[key]:
            xs.append(np.array(obj['input']))
            if 'output' not in obj:
                continue
            ys.append(np.array(obj['output']))
    return xs, ys


# In[ ]:


from skimage.measure import label, regionprops
def make_features(x, has_frame=False):
    def short_flattener(pred):
        str_pred = str([row for row in pred])
        str_pred = str_pred.replace(', ', '')
        str_pred = str_pred.replace('[[', '')
        str_pred = str_pred.replace('][', '|')
        str_pred = str_pred.replace(']]', '')
        return str_pred
    with open("ex.txt", "w") as f:
        f.write(short_flattener(x.tolist()))
    get_ipython().system('./main > /dev/null')
    columns = pd.read_csv('features.tsv', sep='\t').columns
    columns = ["".join (c if c.isalnum() else "_" for c in str(col)) for col in columns]
    df = pd.DataFrame(np.fromfile('features.bin', dtype = [(col, '<f4') for col in columns]))
    
    df['rps4'] = False
    df['rps8'] = False
    labels = label(x, background=-1, connectivity=2)+2
    rps = regionprops(labels, cache=False)
    for r in rps:
        xmin, ymin, xmax, ymax = r.bbox
        df.loc[(df['xmin']==xmin)&(df['ymin']==ymin)&(df['xmax']==xmax)&(df['ymax']==ymax), 'rps8'] = True
    labels = label(x, background=-1, connectivity=1)+2
    rps = regionprops(labels, cache=False)
    for r in rps:
        xmin, ymin, xmax, ymax = r.bbox
        df.loc[(df['xmin']==xmin)&(df['ymin']==ymin)&(df['xmax']==xmax)&(df['ymax']==ymax), 'rps4'] = True
    
    if has_frame:
        df = df[(df['has_frame']==1)|(df['has_frame_1']==1)]
    for col in ['cnt_same_boxes', 'cnt_same_boxes_w_fr', 'cnt_same_boxes_wo_tr', 'ucnt_colors']:
        df[f"{col}_rank"]  = df[col].rank(method="dense")
        df[f"{col}_rank_"] = df[col].rank(method="dense", ascending=False)
    for col in df.columns:
        if 'iou' in col or col in ['has_frame', 'has_frame_1']:
            df[f"{col}_rank"]  = df.groupby([col])['area'].rank(method="dense")
            df[f"{col}_rank_"] = df.groupby([col])['area'].rank(method="dense", ascending=False)
    return df

def predict(train, test, test_input):
    y = train.pop('label')
    model = BaggingClassifier(base_estimator=DecisionTreeClassifier(), n_estimators=100, random_state=4372).fit(train.drop(['xmin','ymin','xmax','ymax'], axis=1), y)
    preds = model.predict_proba(test.drop(['xmin','ymin','xmax','ymax'], axis=1))[:,1]
    
    indexes = np.argsort(preds)[::-1]
    objects,objs,titles = [],[],[]
    for score, (xmin,ymin,xmax,ymax) in zip(preds[indexes], test[['xmin','ymin','xmax','ymax']].astype(int).values[indexes]):
        obj = test_input[xmin:xmax,ymin:ymax]
        str_obj = flattener(obj.tolist())
        if str_obj not in objects:
            objects.append(str_obj)
            objs.append(obj)
            titles.append(str(np.round(score, 4)))
        if len(objects) > 10:
            break
    plot_objects(objs, titles) 
    return objects

def format_features(task):
    train = []
    for ttid, obj in enumerate(task['train']):
        x = np.array(obj['input'])
        y = np.array(obj['output'])
        df = make_features(x)
        df['label'] = False
#         df['tid'] = ttid
        positions = find_sub(x, y)
        for xmin,ymin,xmax,ymax in positions:
            df.loc[(df['xmin']==xmin)&(df['ymin']==ymin)&(df['xmax']==xmax)&(df['ymax']==ymax), 'label'] = True
        train.append(df)
    train = pd.concat(train).reset_index(drop=True)
    return train


# In[ ]:


from tqdm.auto import trange
submission = pd.read_csv(data_path/ 'sample_submission.csv')
problems = submission['output_id'].values
answers = []
for i in trange(len(problems)):
    output_id = problems[i]
    task_id = output_id.split('_')[0]
    pair_id = int(output_id.split('_')[1])
    f = str(test_path / str(task_id + '.json'))
   
    with open(f, 'r') as read_file:
        task = json.load(read_file)
        for key_task in task:
            for obj in task[key_task]:
                for key in obj:
                    obj[key] = np.array(obj[key])
    pred = ''
    if check_subitem(task):
        plot_task(task)
        test_input = np.array(task['test'][pair_id]['input'])
        
        test = make_features(test_input)
        train = format_features(task)
        preds = predict(train, test, test_input)
        objects = []
        for pred in preds:
            if pred not in objects:
                objects.append(pred)
        pred = ' '.join(objects[0:3])
        
    answers.append(pred)
    
submission['output'] = answers
submission.to_csv('submission.csv', index = False)
