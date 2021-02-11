import csv
import io
import clcert_chachagen


def suma_mujeres(lista):
    ret = 0
    for j in range(16):
        ret += lista[j][0]
    return ret

# leer archivo de respuestas recibidas
input_filename = "respuestas.csv"
respuestas_id = [[[], []] for i in range(16)]
with open(input_filename, 'rt') as input_file:
    reader = csv.DictReader(io.StringIO(input_file.read()))
    for row in reader:
        id = int(row['ID'])
        sexo = int(row['SEXO'])
        region = int(row['REGION']) - 1
        respuestas_id[region][sexo].append(id)

# construir tabla de número de respuestas recibidas
respuestas = [[0] * 3 for i in range(16)]
for i in range(16):
    for j in range(2):
        respuestas[i][j] = len(respuestas_id[i][j])
    respuestas[i][2] = respuestas[i][0] + respuestas[i][1]

# escribir .csv con la tabla de número de respuestas recibidas
# output_filename = "total_respuestas.csv"
# output_columns = ['REGION', 'MUJER', 'HOMBRE', 'TOTAL']
# with open(output_filename, 'w') as output_file:
#     writer = csv.DictWriter(output_file, fieldnames=output_columns)
#     writer.writeheader()
#     for i in range(16):
#         writer.writerow({'REGION': i + 1,
#                          'MUJER': respuestas[i][0],
#                          'HOMBRE': respuestas[i][1],
#                          'TOTAL': respuestas[i][2]})

# ejemplo 1
# respuestas = [[12, 9, 21], [10, 20, 30], [8, 14, 22], [13, 25, 38], [55, 59, 114], [24, 15, 39], [25, 26, 51],
#               [34, 31, 65], [22, 19, 41], [12, 14, 26], [5, 5, 10], [4, 6, 10], [200, 250, 450], [12, 5, 17],
#               [12, 20, 32], [7, 7, 14]]

# tabla con la distribución ideal de invitaciones
ideal = [[8, 7, 15], [13, 13, 26], [7, 7, 14], [17, 17, 34], [52, 50, 102], [19, 19, 38], [21, 20, 41],
         [37, 35, 72], [20, 19, 39], [17, 16, 33], [3, 2, 5], [5, 4, 9], [167, 162, 329], [5, 5, 10], [8, 7, 15],
         [9, 9, 18]]

cuota = [[0, 0, 0] for _ in range(16)]
total = 0
excedente = [[0, 0, 0] for _ in range(16)]

# distribuir cupos iniciales
for i in range(16):
    for s in range(2):
        cuota[i][s] = min(ideal[i][s], respuestas[i][s])  # elegir el mínimo entre lo ideal y las respuestas recibidas
        total += cuota[i][s]
        excedente[i][s] = respuestas[i][s] - cuota[i][s]
    # actualizar el total de cuota y excedente
    cuota[i][2] = cuota[i][0] + cuota[i][1]
    excedente[i][2] = excedente[i][0] + excedente[i][1]

# distribuir cupos adicionales (solo si faltan completar 800 personas)
while total < 800:
    alpha = (suma_mujeres(cuota) / total) / 0.51  # factor distribución de sexo (idealmente 51% mujeres)
    beta = [pow(1 - (cuota[i][2] / ideal[i][2]), 2) for i in range(16)]  # factor distribución por región

    # ordenar regiones con respecto a su falta de representación
    delta_beta = [0 if excedente[i][2] == 0
                    else pow(1 - ((cuota[i][2] + 1) / ideal[i][2]), 2) - beta[i] for i in range(16)]
    regiones_necesarias = [delta_beta.index(sorted(delta_beta)[i]) for i in range(16)]

    sexo = 0 if (1 - alpha) > 0 else 1  # sexo necesario para mejorar factor alpha

    exito = False  # variable para detectar que fue agregada una persona en la presente iteración
    while True:
        for r in regiones_necesarias:  # recorrer regiones en orden con respecto a su falta de representación
            if excedente[r][sexo] > 0:
                # existen personas del sexo necesario en la presente región
                cuota[r][sexo] += 1
                cuota[r][2] += 1
                excedente[r][sexo] -= 1
                excedente[r][2] -= 1
                total += 1
                exito = True
                break
            else:
                continue
        if not exito:
            # si no se agregó una persona del sexo necesario, no quedan personas de ese sexo
            sexo = (sexo + 1) % 2  # cambiar de sexo
        else:
            break

# elegir las personas invitadas
invitaciones = [[[], []] for i in range(16)]
chacha_prng = clcert_chachagen.ChaChaGen()
for i in range(16):
    for j in range(2):
        invitaciones[i][j] = chacha_prng.sample(respuestas_id[i][j], cuota[i][j])

# escribir .csv con las invitaciones
output_filename = 'invitaciones.csv'
output_columns = ['ID', 'SEXO', 'REGION']
with open(output_filename, 'w') as output_file:
    writer = csv.DictWriter(output_file, fieldnames=output_columns)
    writer.writeheader()
    for i in range(16):
        for j in range(2):
            for id in sorted(invitaciones[i][j]):
                writer.writerow({'ID': id,
                                 'SEXO': j,
                                 'REGION': i + 1})
