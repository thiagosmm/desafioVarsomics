import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import matplotlib.pyplot as plt

def extracao():
    # parametros para requisição da API
    url = 'https://elasticsearch-saps.saude.gov.br/desc-esus-notifica-estado-*/_search'
    usuario = 'user-public-notificacoes'
    senha = 'Za4qNXdyQNSa9YaA'
    query = {
        "size": 1500
    }

    # requisição para API 
    respostaAPI = requests.get(url, auth=HTTPBasicAuth(usuario, senha), params=query)

    # verifica se a requisição deu certo
    if respostaAPI.status_code == 200:
        dados = respostaAPI.json()
        return dados
    else:
        print('Falha na requisição', respostaAPI.status_code)
        return None

def transformacao(dados):
    registros = []
    for hit in dados['hits']['hits']:
        testes = hit['_source'].get('testes', [])
        dataNotificacao = hit['_source']['dataNotificacao']
        if dataNotificacao > '2020-03-01T00:00:00.000Z': 
            for teste in testes:
                registro = {
                    'dataNotificacao': hit['_source']['dataNotificacao'],
                    'idade': hit['_source']['idade'],
                    'codigoResultadoTeste': teste.get('codigoResultadoTeste'),
                    'sintomas': hit['_source']['sintomas'],
                    'codigoRecebeuVacina': hit['_source']['codigoRecebeuVacina'],
                    'estado': hit['_source']['estado'],
                    'estadoNotificacao': hit['_source']['estadoNotificacao'],
                    'evolucaoCaso': hit['_source']['evolucaoCaso'],
                    'classificacaoFinal': hit['_source']['classificacaoFinal']
                }

                registros.append(registro)

    return registros

def carregamento(dadosTransformados, arquivo):
    df = pd.DataFrame(dadosTransformados)
    df.to_csv(arquivo, index = False)
    
    return df

def analises(df):
#1 qual o estado com a maior proporção de casos confirmados?
    df_casosConfirmados = df[df['classificacaoFinal'].str.contains('Confirmado', case=False, na=False)]
    contEstados = df_casosConfirmados['estado'].value_counts()
    contEstados.plot(kind='pie', figsize=(8, 8), autopct='%1.1f%%')
    plt.title('Proporção de casos confirmados de COVID-19 por estado de residência')
    plt.ylabel('')
    plt.show()

#2 dentre os casos confirmados, qual a proporção de pacientes que receberam 
# ao menos 1 dose de vacina
    contRecebeuVacina = df_casosConfirmados['codigoRecebeuVacina'].value_counts()
    labels= ['1 dose', 'Nenhuma', 'Não informado']
    contRecebeuVacina.plot(kind='pie',labels=labels, figsize=(8,8), autopct='%1.1f%%')
    plt.title('Proporção de pacientes com pelo menos uma dose de vacina dentre os casos confirmados')
    plt.ylabel('')
    plt.show()

#3 como é a distribuição de idade entre os pacientes sintomáticos
# e assintomáticos entre os casos confirmados?

# distribuição para casos sintomáticos
    df_sintomaticos = df_casosConfirmados[df_casosConfirmados['sintomas'] != 'Assintomático']
    contIdadesSintomaticos = df_sintomaticos['idade'].value_counts().sort_index()
    plt.figure(figsize=(12,10))
    contIdadesSintomaticos.plot(kind='bar')
    plt.xlabel('Idade')
    plt.ylabel('Número pacientes')
    plt.title('Distribuição de idade - Pacientes sintomáticos')
    plt.yticks(range(0, contIdadesSintomaticos.max() + 1, 1))
    plt.show()

# distribuição para casos assintomáticos
    df_assintomaticos = df_casosConfirmados[df_casosConfirmados['sintomas'] == 'Assintomático']
    contIdadesAssintomaticos = df_assintomaticos['idade'].value_counts().sort_index()
    plt.figure(figsize=(8,6))
    contIdadesAssintomaticos.plot(kind='bar')
    plt.xlabel('Idade')
    plt.ylabel('Número pacientes')
    plt.title('Distribuição de idade - Pacientes assintomáticos')
    plt.yticks(range(0, contIdadesAssintomaticos.max() + 1, 1))
    plt.show()


#4 Para (pelo menos um) estados a sua escolha, construa uma
# visualização para acompanhar a evolução dos casos ao longo do
# período amostrado. --- selecionar estado, ordenar pela datas
# (notificacao, resultado, encerramento) 


#5 Entre os pacientes sintomáticos, qual o sintoma mais frequente? --- juntar arrays de sintomas e contar cada um
    contSintomas = df_sintomaticos['sintomas'].value_counts()
    contSintomas.plot(kind='pie', figsize=(8, 8), autopct='%1.1f%%')
    plt.title('Frequência de sintomas em pacientes confirmados')
    plt.ylabel('')

def main():
    dados = extracao()
    if dados != None:
        dadosTransformados = transformacao(dados)
        df = carregamento(dadosTransformados, 'arquivo.csv')
        analises(df)
    else: print("Falha na extração")

main()