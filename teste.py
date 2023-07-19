entrada = "010450048-0, 010450049-0"

# Dividir a string em uma lista de elementos separados por vírgula
elementos = entrada.split(", ")

# Adicionar aspas simples em cada elemento da lista
elementos_formatados = ["'" + elemento + "'" for elemento in elementos]

# Juntar os elementos formatados em uma única string, separados por vírgula
saida = ", ".join(elementos_formatados)

print(saida)
