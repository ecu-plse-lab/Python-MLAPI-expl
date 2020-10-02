"""
    Script criado para consolidar fun��es �teis utilizadas na plotagem e personaliza��o de gr�ficos
"""

"""
--------------------------------------------
---------- IMPORTANDO BIBLIOTECAS ----------
--------------------------------------------
"""
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from warnings import filterwarnings
filterwarnings('ignore')
from typing import *
from dataclasses import dataclass
from math import ceil

"""
--------------------------------------------
---------- 1. FORMATA��O DE EIXOS ----------
--------------------------------------------
"""


# Formatando eixos do matplotlib
def format_spines(ax, right_border=True):
    """
    This function sets up borders from an axis and personalize colors

    Input:
        Axis and a flag for deciding or not to plot the right border
    Returns:
        Plot configuration
    """
    # Setting up colors
    ax.spines['bottom'].set_color('#CCCCCC')
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['top'].set_visible(False)
    if right_border:
        ax.spines['right'].set_color('#CCCCCC')
    else:
        ax.spines['right'].set_color('#FFFFFF')
    ax.patch.set_facecolor('#FFFFFF')

# Classe para plotagem dos r�tulos dos dados em gr�ficos de barras
# Refer�ncia: https://towardsdatascience.com/annotating-bar-charts-and-other-matplolib-techniques-cecb54315015
#Alias types to reduce typing, no pun intended
Patch = matplotlib.patches.Patch
PosVal = Tuple[float, Tuple[float, float]]
Axis = matplotlib.axes.Axes
PosValFunc = Callable[[Patch], PosVal]

@dataclass
class AnnotateBars:
    font_size: int = 10
    color: str = "black"
    n_dec: int = 2
    def horizontal(self, ax: Axis, centered=False):
        def get_vals(p: Patch) -> PosVal:
            value = p.get_width()
            div = 2 if centered else 1
            pos = (
                p.get_x() + p.get_width() / div,
                p.get_y() + p.get_height() / 2,
            )
            return value, pos
        ha = "center" if centered else  "left"
        self._annotate(ax, get_vals, ha=ha, va="center")
    def vertical(self, ax: Axis, centered:bool=False):
        def get_vals(p: Patch) -> PosVal:
            value = p.get_height()
            div = 2 if centered else 1
            pos = (p.get_x() + p.get_width() / 2,
                   p.get_y() + p.get_height() / div
            )
            return value, pos
        va = "center" if centered else "bottom"
        self._annotate(ax, get_vals, ha="center", va=va)
    def _annotate(self, ax, func: PosValFunc, **kwargs):
        cfg = {"color": self.color,
               "fontsize": self.font_size, **kwargs}
        for p in ax.patches:
            value, pos = func(p)
            ax.annotate(f"{value:.{self.n_dec}f}", pos, **cfg)

# Definindo fun��es �teis para plotagem dos r�tulos no gr�fico
def make_autopct(values):
    """
    Etapas:
        1. defini��o de fun��o para formata��o dos r�tulos

    Argumentos:
        values -- valores extra�dos da fun��o value_counts() da coluna de an�lise [list]

    Retorno:
        my_autopct -- string formatada para plotagem dos r�tulos
    """

    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))

        return '{p:.1f}%\n({v:d})'.format(p=pct, v=val)

    return my_autopct

"""
--------------------------------------------
---------- 2. PLOTAGENS GR�FICAS -----------
--------------------------------------------
"""


# Fun��o para plotagem de gr�fico de rosca em rela��o a uma vari�vei espec�fica do dataset
def donut_plot(df, col, label_names, ax, text='', colors=['crimson', 'navy'], circle_radius=0.8,
            title=f'Gr�fico de Rosca'):
    """
    Etapas:
        1. defini��o de fun��es �teis para mostrar r�tulos em valor absoluto e porcentagem
        2. cria��o de figura e c�rculo central de raio pr�-definido
        3. plotagem do gr�fico de pizza e adi��o do c�rculo central
        4. configura��o final da plotagem

    Argumentos:
        df -- DataFrame alvo da an�lise [pandas.DataFrame]
        col -- coluna do DataFrame a ser analisada [string]
        label_names -- nomes customizados a serem plotados como labels [list]
        text -- texto central a ser posicionado [string / default: '']
        colors -- cores das entradas [list / default: ['crimson', 'navy']]
        figsize -- dimens�es da plotagem [tupla / default: (8, 8)]
        circle_radius -- raio do c�rculo central [float / default: 0.8]

    Retorno:
        None
    """

    # Retorno dos valores e defini��o da figura
    values = df[col].value_counts().values
    center_circle = plt.Circle((0, 0), circle_radius, color='white')

    # Plotando gr�fico de rosca
    ax.pie(values, labels=label_names, colors=colors, autopct=make_autopct(values))
    ax.add_artist(center_circle)

    # Configurando argumentos do texto central
    kwargs = dict(size=20, fontweight='bold', va='center')
    ax.text(0, 0, text, ha='center', **kwargs)
    ax.set_title(title, size=14, color='dimgrey')


# Fun��o para an�lise da matriz de correla��o
def target_correlation_matrix(data, label_name, ax, n_vars=10, corr='positive', fmt='.2f', cmap='YlGnBu',
                              cbar=True, annot=True, square=True):
    """
    Etapas:
        1. constru��o de correla��o entre as vari�veis
        2. filtragem das top k vari�veis com maior correla��o
        3. plotagem e configura��o da matriz de correla��o

    Argumentos:
        data -- DataFrame a ser analisado [pandas.DataFrame]
        label_name -- nome da coluna contendo a vari�vel resposta [string]
        n_vars -- indicador das top k vari�veis a serem analisadas [int]
        corr -- indicador booleano para plotagem de correla��es ('positive', 'negative') [string]
        fmt -- formato dos n�meros de correla��o na plotagem [string]
        cmap -- color mapping [string]
        figsize -- dimens�es da plotagem gr�fica [tupla]
        cbar -- indicador de plotagem da barra indicadora lateral [bool]
        annot -- indicador de anota��o dos n�meros de correla��o na matriz [bool]
        square -- indicador para redimensionamento quadr�tico da matriz [bool]

    Retorno:
        None
    """

    # Criando matriz de correla��o para a base de dados
    corr_mx = data.corr()

    # Retornando apenas as top k vari�veis com maior correla��o frente a vari�vel resposta
    if corr == 'positive':
        corr_cols = list(corr_mx.nlargest(n_vars+1, label_name)[label_name].index)
        title = f'Top {n_vars} Features - Correla��o Positiva com o Target'
    elif corr == 'negative':
        corr_cols = list(corr_mx.nsmallest(n_vars+1, label_name)[label_name].index)
        corr_cols = [label_name] + corr_cols[:-1]
        title = f'Top {n_vars} Features - Correla��o Negativa com o Target'
        cmap = 'magma'

    corr_data = np.corrcoef(data[corr_cols].values.T)

    # Construindo plotagem da matriz
    sns.heatmap(corr_data, ax=ax, cbar=cbar, annot=annot, square=square, fmt=fmt, cmap=cmap,
                yticklabels=corr_cols, xticklabels=corr_cols)
    ax.set_title(title, size=14, color='dimgrey', pad=20)

    return


# Distplot para compara��o de densidade das features baseadas na vari�vel target
def distplot(df, features, fig_cols, hue=False, color=['crimson', 'darkslateblue'], hist=False, figsize=(16, 12)):
    """
    Etapas:
        1. cria��o de figura de acordo com as especifica��es dos argumentos
        2. la�o para plotagem de boxplot por eixo
        3. formata��o gr�fica
        4. valida��o de eixos excedentes

    Argumentos:
        df -- base de dados para plotagem [pandas.DataFrame]
        features -- conjunto de colunas a serem avaliadas [list]
        fig_cols -- especifica��es da figura do matplotlib [int]
        hue -- vari�vel resposta contida na base [string -- default: False]
        color_list -- cores para cada classe nos gr�ficos [list - default: ['crimson', 'darkslateblue']]
        hist -- indicador de plotagem das faixas do histograma [bool - default: False]
        figsize -- dimens�es da plotagem [tupla - default: (16, 12)]

    Retorno:
        None
    """

    # Definindo vari�veis de controle
    n_features = len(features)
    fig_cols = fig_cols
    fig_rows = ceil(n_features / fig_cols)
    i, j, color_idx = (0, 0, 0)

    # Plotando gr�ficos
    fig, axs = plt.subplots(nrows=fig_rows, ncols=fig_cols, figsize=figsize)

    # Percorrendo por cada uma das features
    for col in features:
        try:
            ax = axs[i, j]
        except:
            ax = axs[j]
        target_idx = 0

        # Plotando, para cada eixo, um gr�fico por classe target
        if hue != False:
            for classe in df[hue].value_counts().index:
                df_hue = df[df[hue] == classe]
                sns.distplot(df_hue[col], color=color[target_idx], hist=hist, ax=ax, label=classe)
                target_idx += 1
        else:
            sns.distplot(df[col], color=color, hist=hist, ax=ax)

        # Incrementando �ndices
        j += 1
        if j == fig_cols:
            j = 0
            i += 1

        # Customizando plotagem
        ax.set_title(f'Feature: {col}', color='dimgrey', size=14)
        plt.setp(ax, yticks=[])
        sns.set(style='white')
        sns.despine(left=True)

    # Tratando caso apartado: figura(s) vazia(s)
    i, j = (0, 0)
    for n_plots in range(fig_rows * fig_cols):

        # Se o �ndice do eixo for maior que a quantidade de features, elimina as bordas
        if n_plots >= n_features:
            try:
                axs[i][j].axis('off')
            except TypeError as e:
                axs[j].axis('off')

        # Incrementando
        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    # Finalizando customiza��o
    plt.tight_layout()
    plt.show()


# Fun��o para plotagem de stripplot
def stripplot(df, features, fig_cols, hue=False, palette='viridis', figsize=(16, 12)):
    """
    Etapas:
        1. cria��o de figura de acordo com as especifica��es dos argumentos
        2. la�o para plotagem de stripplot por eixo
        3. formata��o gr�fica
        4. valida��o de eixos excedentes

    Argumentos:
        df -- base de dados para plotagem [pandas.DataFrame]
        features -- conjunto de colunas a serem avaliadas [list]
        fig_cols -- especifica��es da figura do matplotlib [int]
        hue -- vari�vel resposta contida na base [string - default: False]
        palette -- paleta de cores [string / lista - default: 'viridis']
        figsize -- dimens�es da figura de plotagem [tupla - default: (16, 12)]

    Retorno:
        None
    """

    # Definindo vari�veis de controle
    n_features = len(features)
    fig_cols = fig_cols
    fig_rows = ceil(n_features / fig_cols)
    i, j, color_idx = (0, 0, 0)

    # Plotando gr�ficos
    fig, axs = plt.subplots(nrows=fig_rows, ncols=fig_cols, figsize=figsize)

    # Plotando gr�fico
    for col in features:
        try:
            ax = axs[i, j]
        except:
            ax = axs[j]

        # Plotando gr�fico atribuindo a vari�vel target como hue
        if hue != False:
            sns.stripplot(x=df[hue], y=df[col], ax=ax, palette=palette)
        else:
            sns.stripplot(y=df[col], ax=ax, palette=palette)

        # Formatando gr�fico
        format_spines(ax, right_border=False)
        ax.set_title(f'Feature: {col.upper()}', size=14, color='dimgrey')
        plt.tight_layout()

        # Incrementando �ndices
        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    # Tratando caso apartado: figura(s) vazia(s)
    i, j = (0, 0)
    for n_plots in range(fig_rows * fig_cols):

        # Se o �ndice do eixo for maior que a quantidade de features, elimina as bordas
        if n_plots >= n_features:
            try:
                axs[i][j].axis('off')
            except TypeError as e:
                axs[j].axis('off')

        # Incrementando
        j += 1
        if j == fig_cols:
            j = 0
            i += 1


def boxenplot(df, features, fig_cols, hue=False, palette='viridis', figsize=(16, 12)):
    """
    Etapas:
        1. cria��o de figura de acordo com as especifica��es dos argumentos
        2. la�o para plotagem de boxplot por eixo
        3. formata��o gr�fica
        4. valida��o de eixos excedentes

    Argumentos:
        df -- base de dados para plotagem [pandas.DataFrame]
        features -- conjunto de colunas a serem avaliadas [list]
        fig_cols -- especifica��es da figura do matplotlib [int]
        hue -- vari�vel resposta contida na base [string - default: False]
        palette -- paleta de cores [string / lista - default: 'viridis']
        figsize -- dimens�es da figura de plotagem [tupla - default: (16, 12)]

    Retorno:
        None
    """

    # Definindo vari�veis de controle
    n_features = len(features)
    fig_rows = ceil(n_features / fig_cols)
    i, j, color_idx = (0, 0, 0)

    # Plotando gr�ficos
    fig, axs = plt.subplots(nrows=fig_rows, ncols=fig_cols, figsize=figsize)

    # Plotando gr�fico
    for col in features:
        try:
            ax = axs[i, j]
        except:
            ax = axs[j]

        # Plotando gr�fico atribuindo a vari�vel target como hue
        if hue != False:
            sns.boxenplot(x=df[hue], y=df[col], ax=ax, palette=palette)
        else:
            sns.boxenplot(y=df[col], ax=ax, palette=palette)

        # Formatando gr�fico
        format_spines(ax, right_border=False)
        ax.set_title(f'Feature: {col.upper()}', size=14, color='dimgrey')
        plt.tight_layout()

        # Incrementando �ndices
        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    # Tratando caso apartado: figura(s) vazia(s)
    i, j = (0, 0)
    for n_plots in range(fig_rows * fig_cols):

        # Se o �ndice do eixo for maior que a quantidade de features, elimina as bordas
        if n_plots >= n_features:
            try:
                axs[i][j].axis('off')
            except TypeError as e:
                axs[j].axis('off')

        # Incrementando
        j += 1
        if j == fig_cols:
            j = 0
            i += 1


# Fun��o respons�vel por plotar volumetria de uma vari�vel categ�rica (quebra por hue � opcional)
def countplot(df, feature, order=True, hue=False, label_names=None, palette='plasma', colors=['darkgray', 'navy'],
              figsize=(12, 5), loc_legend='lower left', width=0.75, sub_width=0.3, sub_size=12):
    """
    Etapas:
        1. customiza��o da plotagem de acordo com a presen�a (ou n�o) do par�metro hue
        2. defini��o das figuras e plotagem dos gr�ficos adequados
        3. customiza��o da plotagem

    Argumentos:
        df -- DataFrame alvo da an�lise [pandas.DataFrame]
        feature -- coluna a ser analisada [string]
        order -- flag booleano pra indicar a ordena��o da plotagem [bool - default: True]
        hue -- par�metro de quebra de an�lise [string - default: False]
        label_names -- descri��o dos labels a serem colocados na legenda [list - default: None]
        palette -- paleta de cores a ser utilizada no plot singular da vari�vel [string - default: 'viridis']
        colors -- cores a serem utilizadas no plot quebrado por hue [list - default: ['darkgray', 'navy']]
        figsize -- dimens�es da plotagem [tupla - default: (15, 5)]
        loc_legend -- posi��o da legenda em caso de plotagem por hue [string - default: 'best']
        width -- largura das barras em caso de plotagem por hue [float - default: 0.5]
        sub_width -- par�metro de alinhamento dos r�tulos em caso de plotagem por hue [float - default: 0.3]

    Retorno:
        None
    """

    # Verificando plotagem por quebra de alguma vari�vel categ�rica
    ncount = len(df)
    if hue != False:
        # Redifinindo dimens�es e plotando gr�fico solo + versus vari�vel categ�rica
        figsize = (figsize[0], figsize[1] * 2)
        fig, axs = plt.subplots(nrows=2, ncols=1, figsize=figsize)
        if order:
            sns.countplot(x=feature, data=df, palette=palette, ax=axs[0], order=df[feature].value_counts().index)
        else:
            sns.countplot(x=feature, data=df, palette=palette, ax=axs[0])

        # Plotando gr�fico de an�lise por hue (stacked bar chart)
        feature_rate = pd.crosstab(df[feature], df[hue])
        percent_df = feature_rate.div(feature_rate.sum(1).astype(float), axis=0)
        if order:
            sort_cols = list(df[feature].value_counts().index)
            sorter_index = dict(zip(sort_cols, range(len(sort_cols))))
            percent_df['rank'] = percent_df.index.map(sorter_index)
            percent_df = percent_df.sort_values(by='rank')
            percent_df = percent_df.drop('rank', axis=1)
            percent_df.plot(kind='bar', stacked=True, ax=axs[1], color=colors, width=width)
        else:
            percent_df.plot(kind='bar', stacked=True, ax=axs[1], color=colors, width=width)
        # sns.countplot(x=feature, data=df, palette=colors, hue=hue, ax=axs[1], order=df[feature].value_counts().index)

        # Inserindo r�tulo de percentual para gr�fico singular
        for p in axs[0].patches:
            # Coletando par�metros e inserindo no gr�fico
            x = p.get_bbox().get_points()[:, 0]
            y = p.get_bbox().get_points()[1, 1]
            axs[0].annotate('{:.1f}%'.format(100. * y / ncount), (x.mean(), y), ha='center', va='bottom',
                            size=sub_size)

        # Inserindo r�tulo de percentual para gr�fico hue
        for p in axs[1].patches:
            # Coletando par�metros
            height = p.get_height()
            width = p.get_width()
            x = p.get_x()
            y = p.get_y()

            # Formatando par�metros coletados e inserindo no gr�fico
            label_text = f'{round(100 * height, 1)}%'
            label_x = x + width - sub_width
            label_y = y + height / 2
            axs[1].text(label_x, label_y, label_text, ha='center', va='center', color='white', fontweight='bold',
                        size=sub_size)

        # Definindo t�tulos
        axs[0].set_title(f'An�lise de Volumetria da Vari�vel {feature}', size=14, color='dimgrey', pad=20)
        axs[0].set_ylabel('Volumetria')
        axs[1].set_title(f'An�lise de Volumetria da Vari�vel {feature} por {hue}', size=14, color='dimgrey', pad=20)
        axs[1].set_ylabel('Percentual')

        # Formatando eixo de cada uma das plotagens
        for ax in axs:
            format_spines(ax, right_border=False)

        # Definindo legenda para hue
        plt.legend(loc=loc_legend, title=f'{hue}', labels=label_names)

    else:
        # Plotagem �nica: sem quebra por vari�vel hue
        fig, ax = plt.subplots(figsize=figsize)
        if order:
            sns.countplot(x=feature, data=df, palette=palette, ax=ax, order=df[feature].value_counts().index)
        else:
            sns.countplot(x=feature, data=df, palette=palette, ax=ax)

            # Formatando eixos
        ax.set_ylabel('Volumetria')
        format_spines(ax, right_border=False)

        # Inserindo r�tulo de percentual
        for p in ax.patches:
            x = p.get_bbox().get_points()[:, 0]
            y = p.get_bbox().get_points()[1, 1]
            ax.annotate('{:.1f}%'.format(100. * y / ncount), (x.mean(), y), ha='center', va='bottom')

        # Definindo t�tulo
        ax.set_title(f'An�lise de Volumetria da Vari�vel {feature}', size=14, color='dimgrey')

    # Configura��es finais
    plt.tight_layout()
    plt.show()

# Fun��o respons�vel por plotar volumetria de uma �nica vari�vel categ�rica em formato atualizado
def single_countplot(df, ax, x=None, y=None, order=True, hue=False, palette='plasma', width=0.75, sub_width=0.3,
                     sub_size=12):
    """
    Par�metros
    ----------
    classifiers: conjunto de classificadores em forma de dicion�rio [dict]
    X: array com os dados a serem utilizados no treinamento [np.array]
    y: array com o vetor target do modelo [np.array]

    Retorno
    -------
    None
    """

    # Verificando plotagem por quebra de alguma vari�vel categ�rica
    ncount = len(df)
    if x:
        col = x
    else:
        col = y
    if hue != False:
        if order:
            sns.countplot(x=x, y=y, data=df, palette=palette, ax=ax, order=df[col].value_counts().index, hue=hue)
        else:
            sns.countplot(x=x, y=y, data=df, palette=palette, ax=ax, hue=hue)
    else:
        if order:
            sns.countplot(x=x, y=y, data=df, palette=palette, ax=ax, order=df[col].value_counts().index)
        else:
            sns.countplot(x=x, y=y, data=df, palette=palette, ax=ax)

    # Formatando eixos
    format_spines(ax, right_border=False)

    # Inserindo r�tulo de percentual
    if x:
        for p in ax.patches:
            x = p.get_bbox().get_points()[:, 0]
            y = p.get_bbox().get_points()[1, 1]
            ax.annotate('{}\n{:.1f}%'.format(int(y), 100. * y / ncount), (x.mean(), y), ha='center', va='bottom')
    else:
        for p in ax.patches:
            x = p.get_bbox().get_points()[1, 0]
            y = p.get_bbox().get_points()[:, 1]
            ax.annotate('{} ({:.1f}%)'.format(int(x), 100. * x / ncount), (x, y.mean()), va='center')


# Fun��o para plotagem de volumetria das vari�veis categ�ricas do conjunto de dados
def catplot_analysis(df_categorical, fig_cols=3, hue=False, palette='viridis', figsize=(16, 10)):
    """
    Etapas:
        1. retorno das vari�veis categ�ricas do conjunto de dados
        2. parametriza��o de vari�veis de plotagem
        3. aplica��o de la�os de repeti��o para plotagens / formata��o

    Argumentos:
        df -- conjunto de dados a ser analisado [pandas.DataFrame]
        fig_cols -- quantidade de colunas da figura matplotlib [int]

    Retorno:
        None
    """

    # Retornando par�metros para organiza��o da figura
    if hue != False:
        cat_features = list(df_categorical.drop(hue, axis=1).columns)
    else:
        cat_features = list(df_categorical.columns)

    total_cols = len(cat_features)
    fig_cols = fig_cols
    fig_rows = ceil(total_cols / fig_cols)
    ncount = len(cat_features)

    # Retornando par�metros para organiza��o da figura
    sns.set(style='white', palette='muted', color_codes=True)
    total_cols = len(cat_features)
    fig_rows = ceil(total_cols / fig_cols)

    # Criando figura de plotagem
    fig, axs = plt.subplots(nrows=fig_rows, ncols=fig_cols, figsize=(figsize))
    i, j = 0, 0

    # La�o de repeti��o para plotagem categ�rica
    for col in cat_features:
        # Indexando vari�veis e plotando gr�fico
        try:
            ax = axs[i, j]
        except:
            ax = axs[j]
        if hue != False:
            sns.countplot(y=col, data=df_categorical, palette=palette, ax=ax, hue=hue,
                          order=df_categorical[col].value_counts().index)
        else:
            sns.countplot(y=col, data=df_categorical, palette=palette, ax=ax,
                          order=df_categorical[col].value_counts().index)

        # Customizando gr�fico
        format_spines(ax, right_border=False)
        AnnotateBars(n_dec=0, color='dimgrey').horizontal(ax)
        ax.set_title(col)

        # Incrementando �ndices de eixo
        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    # Tratando caso apartado: figura(s) vazia(s)
    i, j = (0, 0)
    for n_plots in range(fig_rows * fig_cols):

        # Se o �ndice do eixo for maior que a quantidade de features, elimina as bordas
        if n_plots >= len(cat_features):
            try:
                axs[i][j].axis('off')
            except TypeError as e:
                axs[j].axis('off')

        # Incrementando
        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    plt.tight_layout()
    plt.show()


# Fun��o para plotagem de volumetria das vari�veis categ�ricas do conjunto de dados
def numplot_analysis(df_numerical, fig_cols=3, color_sequence=['darkslateblue', 'mediumseagreen', 'darkslateblue'],
                     hue=False, color_hue=['darkslateblue', 'crimson'], hist=False):
    """
    Etapas:
        1. retorno das vari�veis categ�ricas do conjunto de dados
        2. parametriza��o de vari�veis de plotagem
        3. aplica��o de la�os de repeti��o para plotagens / formata��o

    Argumentos:
        df -- conjunto de dados a ser analisado [pandas.DataFrame]
        fig_cols -- quantidade de colunas da figura matplotlib [int]

    Retorno:
        None
    """

    # Configurando sets do seaborn
    sns.set(style='white', palette='muted', color_codes=True)

    # Criando um DataFrame de vari�veis categ�ricas
    #num_features = [col for col, dtype in df.dtypes.items() if dtype != 'object']
    #df_numerical = df.loc[:, num_features]

    # Retornando par�metros para organiza��o da figura
    if hue != False:
        num_features = list(df_numerical.drop(hue, axis=1).columns)
    else:
        num_features = list(df_numerical.columns)

    total_cols = len(num_features)
    fig_cols = fig_cols
    fig_rows = ceil(total_cols / fig_cols)

    # Criando figura de plotagem
    fig, axs = plt.subplots(nrows=fig_rows, ncols=fig_cols, figsize=(fig_cols * 5, fig_rows * 4.5))
    sns.despine(left=True)
    i, j = 0, 0

    # La�o de repeti��o para plotagem categ�rica
    color_idx = 0
    for col in num_features:
        # Indexando vari�veis e plotando gr�fico
        try:
            ax = axs[i, j]
        except:
            ax = axs[j]
        target_idx = 0

        if hue != False:
            for classe in df_numerical[hue].value_counts().index:
                df_hue = df_numerical[df_numerical[hue] == classe]
                sns.distplot(df_hue[col], color=color_hue[target_idx], hist=hist, ax=ax, label=classe)
                target_idx += 1
                ax.set_title(col)
        else:
            sns.distplot(df_numerical[col], color=color_sequence[color_idx], hist=hist, ax=ax)
            ax.set_title(col, color=color_sequence[color_idx])

        # Customizando gr�fico
        format_spines(ax, right_border=False)

        # Incrementando �ndices de eixo
        color_idx += 1
        j += 1
        if j == fig_cols:
            j = 0
            i += 1
            color_idx = 0

    # Tratando caso apartado: figura(s) vazia(s)
    i, j = (0, 0)
    for n_plots in range(fig_rows * fig_cols):

        # Se o �ndice do eixo for maior que a quantidade de features, elimina as bordas
        if n_plots >= len(num_features):
            try:
                axs[i][j].axis('off')
            except TypeError as e:
                axs[j].axis('off')

        # Incrementando
        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    plt.setp(axs, yticks=[])
    plt.tight_layout()
    plt.show()


# Fun��o para plotagem de representatividade de cada categoria quanto a um hue espec�fico
def catplot_percentage_analysis(df_categorical, hue, fig_cols=2, palette='viridis', figsize=(16, 10)):
    """
    Etapas:
        1. retorno das vari�veis categ�ricas do conjunto de dados
        2. parametriza��o de vari�veis de plotagem
        3. aplica��o de la�os de repeti��o para plotagens / formata��o

    Argumentos:
        df -- conjunto de dados a ser analisado [pandas.DataFrame]
        fig_cols -- quantidade de colunas da figura matplotlib [int]

    Retorno:
        None
    """
 
    # Retornando par�metros para organiza��o da figura
    sns.set(style='white', palette='muted', color_codes=True)
    cat_features = list(df_categorical.drop(hue, axis=1).columns)
    total_cols = len(cat_features)
    fig_rows = ceil(total_cols / fig_cols)

    # Criando figura de plotagem
    fig, axs = plt.subplots(nrows=fig_rows, ncols=fig_cols, figsize=(figsize))
    i, j = 0, 0

    # La�o de repeti��o para plotagem categ�rica
    for col in cat_features:
        # Indexando vari�veis e plotando gr�fico
        try:
            ax = axs[i, j]
        except:
            ax = axs[j]

        # Aplicando crosstab para an�lise de representatividade da categoria
        col_to_hue = pd.crosstab(df_categorical[col], df_categorical[hue])
        col_to_hue.div(col_to_hue.sum(1).astype(float), axis=0).plot(kind='barh', stacked=True, ax=ax,
                                                                     colors=palette)

        # Customizando gr�fico
        format_spines(ax, right_border=False)
        ax.set_title(col)
        ax.set_ylabel('')

        # Incrementando �ndices de eixo
        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    # Tratando caso apartado: figura(s) vazia(s)
    i, j = (0, 0)
    for n_plots in range(fig_rows * fig_cols):

        # Se o �ndice do eixo for maior que a quantidade de features, elimina as bordas
        if n_plots >= len(cat_features):
            try:
                axs[i][j].axis('off')
            except TypeError as e:
                axs[j].axis('off')

        # Incrementando
        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    plt.tight_layout()
    plt.show()


def mean_sum_analysis(df, group_col, value_col, orient='vertical', palette='plasma', figsize=(15, 6)):
    """
    Par�metros
    ----------
    classifiers: conjunto de classificadores em forma de dicion�rio [dict]
    X: array com os dados a serem utilizados no treinamento [np.array]
    y: array com o vetor target do modelo [np.array]

    Retorno
    -------
    None
    """

    # Grouping data
    df_mean = df.groupby(group_col, as_index=False).mean()
    df_sum = df.groupby(group_col, as_index=False).sum()

    # Sorting grouped dataframes
    df_mean.sort_values(by=value_col, ascending=False, inplace=True)
    sorter = list(df_mean[group_col].values)
    sorter_idx = dict(zip(sorter, range(len(sorter))))
    df_sum['mean_rank'] = df_mean[group_col].map(sorter_idx)
    df_sum.sort_values(by='mean_rank', inplace=True)
    df_sum.drop('mean_rank', axis=1, inplace=True)

    # Plotting data
    fig, axs = plt.subplots(ncols=2, figsize=figsize)
    if orient == 'vertical':
        sns.barplot(x=value_col, y=group_col, data=df_mean, ax=axs[0], palette=palette)
        sns.barplot(x=value_col, y=group_col, data=df_sum, ax=axs[1], palette=palette)
        AnnotateBars(n_dec=0, font_size=12, color='black').horizontal(axs[0])
        AnnotateBars(n_dec=0, font_size=12, color='black').horizontal(axs[1])
    elif orient == 'horizontal':
        sns.barplot(x=group_col, y=value_col, data=df_mean, ax=axs[0], palette=palette)
        sns.barplot(x=group_col, y=value_col, data=df_sum, ax=axs[1], palette=palette)
        AnnotateBars(n_dec=0, font_size=12, color='black').vertical(axs[0])
        AnnotateBars(n_dec=0, font_size=12, color='black').vertical(axs[1])

    # Customizing plot
    for ax in axs:
        format_spines(ax, right_border=False)
        ax.set_ylabel('')
    axs[0].set_title(f'Mean of {value_col} by {group_col}', size=14, color='dimgrey')
    axs[1].set_title(f'Sum of {value_col} by {group_col}', size=14, color='dimgrey')

    plt.tight_layout()
    plt.show()

"""
--------------------------------------------
-------- 3. AN�LISES EM DATAFRAMES ---------
--------------------------------------------
"""


def data_overview(df, corr=False, label_name=None, sort_by='qtd_null', thresh_percent_null=0, thresh_corr_label=0):
    """
    Etapas:
        1. levantamento de atributos com dados nulos no conjunto
        2. an�lise do tipo primitivo de cada atributo
        3. an�lise da quantidade de entradas em caso de atributos categ�ricos
        4. extra��o da correla��o pearson com o target para cada atributo
        5. aplica��o de regras definidas nos argumentos
        6. retorno do dataset de overview criado

    Argumentos:
        df -- DataFrame a ser analisado [pandas.DataFrame]
        label_name -- nome da vari�vel target [string]
        sort_by -- coluna de ordena��o do dataset de overview [string - default: 'qtd_null']
        thresh_percent_null -- filtro de dados nulos [int - default: 0]
        threh_corr_label -- filtro de correla��o com o target [int - default: 0]

    Retorno
        df_overview -- dataet consolidado contendo an�lise das colunas [pandas.DataFrame]
    """

    # Criando DataFrame com informa��es de dados nulos
    df_null = pd.DataFrame(df.isnull().sum()).reset_index()
    df_null.columns = ['feature', 'qtd_null']
    df_null['percent_null'] = df_null['qtd_null'] / len(df)

    # Retornando tipo primitivo e qtd de entradas para os categ�ricos
    df_null['dtype'] = df_null['feature'].apply(lambda x: df[x].dtype)
    df_null['qtd_cat'] = [len(df[col].value_counts()) if df[col].dtype == 'object' else 0 for col in
                          df_null['feature'].values]

    if corr:
        # Extraindo informa��o de correla��o com o target
        label_corr = pd.DataFrame(df.corr()[label_name])
        label_corr = label_corr.reset_index()
        label_corr.columns = ['feature', 'target_pearson_corr']

        # Unindo informa��es
        df_null_overview = df_null.merge(label_corr, how='left', on='feature')
        df_null_overview.query('target_pearson_corr > @thresh_corr_label')
    else:
        df_null_overview = df_null

    # Filtrando dados nulos de acordo com limiares
    df_null_overview.query('percent_null > @thresh_percent_null')

    # Ordenando DataFrame
    df_null_overview = df_null_overview.sort_values(by=sort_by, ascending=False)
    df_null_overview = df_null_overview.reset_index(drop=True)

    return df_null_overview