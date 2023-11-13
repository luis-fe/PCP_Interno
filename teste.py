import pandas as pd

# Seu DataFrame
data = {'coluna1': ['a', 'b'], 'coluna2': ['10, 20, 30', '5']}
df = pd.DataFrame(data)

# Obtendo o valor do índice 0 da coluna1
valor_coluna1 = df.loc[0, 'coluna1']

# Obtendo o primeiro valor da lista na coluna2
valor_coluna2 = df.loc[1, 'coluna2'].split(', ')[0]

# Imprimindo os resultados
print(f"valor do índice 0 da coluna1 = \"{valor_coluna1}\"")
print(f"valor do índice 0 da coluna2 e primeira ocorrência = \"{valor_coluna2}\"")
