import pandas as pd

# Exemplo de DataFrame com a coluna "coluna1"
data = {'coluna1': ['aa', 'bb', 'cc', 'dd']}
df = pd.DataFrame(data)

# Transformar os valores da coluna em uma única string
resultado = '({})'.format(', '.join(["'{}'".format(valor) for valor in df['coluna1']]))

print(type(resultado))
