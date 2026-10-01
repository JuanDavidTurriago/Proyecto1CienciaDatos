"""Ocho figuras que usan exclusivamente resultados de las seis consultas SQL."""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from .consultas import interpretar

def visualizar(numero, resultados):
    sns.set_theme(style='whitegrid',palette='colorblind',font_scale=1.0)
    fig,ax=plt.subplots(figsize=(10,5.5),layout='constrained')
    q1,q2,q3,q4,q5,q6=resultados
    if numero == 1:
        x=pd.to_datetime(dict(year=q1.anio,month=q1.mes,day=1))
        ax.plot(x,q1.cantidad,color='#176E86',linewidth=2)
        ax.set(title='Cantidad mensual registrada en el archivo',xlabel='Mes de la fecha registrada',ylabel='Cantidad registrada (unidades)')
        insight=interpretar(0,q1)
    elif numero == 2:
        d=q2.head(10).sort_values('cantidad')
        ax.barh(d.departamento,d.cantidad,color='#176E86')
        ax.set(title='Diez departamentos con mayor cantidad registrada',xlabel='Cantidad registrada (unidades)',ylabel='Departamento')
        insight=interpretar(1,q2)
    elif numero == 3:
        d=q3.groupby(['anio','zona']).cantidad.sum().unstack(fill_value=0)
        d.plot.bar(ax=ax,rot=0,color=['#E49A38','#176E86'])
        ax.set(title='Cantidad registrada por año y zona',xlabel='Año de la fecha registrada',ylabel='Cantidad registrada (unidades)')
        ax.legend(title='Zona')
        g=q3.groupby('zona').cantidad.sum().sort_values(ascending=False)
        insight=f'La zona {g.index[0]} concentra {g.iloc[0]:,.0f} unidades ({100*g.iloc[0]/g.sum():.2f}%). Las comparaciones anuales están condicionadas por la cobertura de fechas del archivo.'
    elif numero == 4:
        d=q4.groupby('arma_medio').cantidad.sum().sort_values()
        ax.barh(d.index,d.values,color='#176E86')
        ax.set(title='Cantidad registrada por arma o medio',xlabel='Cantidad registrada (unidades)',ylabel='Arma o medio')
        insight=interpretar(3,q4)
    elif numero == 5:
        ax.scatter(q5.urbana,q5.rural,alpha=.5,s=23,color='#176E86')
        for _,r in q5.head(3).iterrows():
            ax.annotate(r.municipio,(r.urbana,r.rural),fontsize=8,xytext=(4,4),textcoords='offset points')
        ax.set(title='Cantidad urbana y rural por municipio',xlabel='Cantidad urbana acumulada (unidades)',ylabel='Cantidad rural acumulada (unidades)')
        insight=interpretar(4,q5)
    elif numero == 6:
        sns.histplot(q6.cantidad,bins=30,kde=True,ax=ax,color='#176E86')
        ax.set(title='Distribución de cantidades por departamento y mes',xlabel='Cantidad por departamento-mes (unidades)',ylabel='Frecuencia (combinaciones departamento-mes)')
        insight=interpretar(5,q6)
    elif numero == 7:
        departamentos=q2.head(6).departamento.tolist()
        d=q6[q6.departamento.isin(departamentos)]
        sns.boxplot(data=d,x='cantidad',y='departamento',order=departamentos,ax=ax,color='#72B1C3')
        ax.set(title='Variación mensual en los seis primeros departamentos',xlabel='Cantidad mensual (unidades)',ylabel='Departamento')
        medianas=d.groupby('departamento').cantidad.median().sort_values(ascending=False)
        insight=f'Entre estos seis departamentos, {medianas.index[0]} tiene la mayor mediana mensual: {medianas.iloc[0]:.1f} unidades. Las cajas muestran dispersión y los puntos extremos no se eliminan; todos provienen de Q6.'
    else:
        d=q3.groupby(['anio','sexo']).cantidad.sum().unstack(fill_value=0)
        sns.heatmap(d,annot=True,fmt='.0f',cmap='Blues',ax=ax,cbar_kws={'label':'Cantidad registrada (unidades)'})
        ax.set(title='Cantidad registrada por año y sexo',xlabel='Sexo registrado',ylabel='Año de la fecha registrada')
        g=q3.groupby('sexo').cantidad.sum().sort_values(ascending=False)
        insight=f'La categoría {g.index[0]} reúne {g.iloc[0]:,.0f} unidades ({100*g.iloc[0]/g.sum():.2f}%). Se conserva SIN ESTABLECER como categoría explícita; el gráfico no estima riesgo por sexo.'
    fig.text(.5,-.045,'Fuente: archivo aportado por el grupo. Cobertura temporal pendiente de verificación.',ha='center',fontsize=9,color='#555555')
    return fig,insight
