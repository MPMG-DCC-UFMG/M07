# Instruções

## Indexar csvs
Para indexar um csv em um indice especifico use o elastic_indexer.py.
O script indexa uma lista de csvs dados e/ou todos os documentos csvs de uma dada pasta (note que ele não confere se o arquivo é um csv ou esta na formatação correta).
O nome das colunas do csv devem bater com o nome dos campos do indice no qual se deseja indexar os dados.
Existem duas formas de se indexar os dados, simple e parallel, que usam respectivamente os metodos helpers.bulk e helpers.parallel_bulk do elasticsearch client.

Para indexar um csv usar o scrip ```python elastic_indexer.py```, que conta com os seguintes argumentos:
```
  -strategy
  -index
  -f
  -d
  -t
```

```-strategy``` deve-se escolher entre uma das estrategias apresentadas: ```simple``` ou ```parallel```;
```-index``` deve-se dar o nome do indice no qual se deseja indexar os dados;
```-f```, opicional, deve-se dar uma lista de nomes de arquivos csv que se deseja indexar;
```-d```, opicional, deve-se uma lista de nomes de diretorios, nos quais existam somente arquivos csvs que se deseja indexar;
```-t``` define o numero de Threadpools a se usar quando se escolhe a estrategia ```parallel```, o defaut pe 4.

## update_mapping
Ao rodar ```python update_mapping.py```, para cada indice no arquivo mappings.json, o script verifica se o existe alguma diferença entre esse indice e o indice do elasticsearch, caso tenha o indice existente no elastic é apagado. Caso o indice tenha sido apagado ou ele no exista no elasticsearch, é criado um novo indice com o mapping atualizado e os csvs nas respectivas pastas de cada indice. Caso nenhum arquivo exista na pasta, nada é feito.
Nota: As pastas de cada indice devem estar nomeadas com o nome do indice e dentro de uma pasta indexer/indices, note que ao rodar o programa sem existir nenhuma dessas pastas, ele automaticamente ira cria-las da forma especificada.
Quando um indice é criado, o settings presentes no aquivo additional_settings.json são inseridos.
Caso deseje forçar a reindexação de um indice use o argumento ```-force_reindexation```, que deve vir seguido de uma lista de indices que se deseja reindexar. 
Caso deseje forçar a atualização dos settings use o argumento ```-update_settings```, que deve ser seguido de uma lista de indices que se deseja atualizar os settings.

