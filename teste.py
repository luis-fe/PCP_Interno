import pandas as pd

# Seu DataFrame original
data = {'produto': ['a', 'b', 'b', 'c', 'c','c', 'e'],
        'necessidade': [4, 1, 2, 3, 1, 2, 1],
        'estoque': [10, 2, 2, 4, 4, 4, 1]}
df = pd.DataFrame(data)

# Ordene o DataFrame pelo produto para garantir que o cálculo seja feito corretamente
df = df.sort_values(by=['produto'])



# Calcule o estoque novo com base na necessidade e no estoque atual
for idx, row in df.iterrows():
    produto = row['produto']
    necessidade = row['necessidade']
    estoque_atual = row['estoque']


    # Atualize o estoque da próxima linha com o valor calculado
    if idx < len(df) - 1 and df.at[idx + 1, 'produto'] == produto:
        df.at[idx + 1, 'estoque'] = max(0, estoque_atual - necessidade)

# Exiba o DataFrame resultante
print(df)
