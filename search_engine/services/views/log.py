import time
from datetime import datetime, timedelta
import random
import string
import hashlib
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from services.models import LogBusca, LogSearchClick, Document


@csrf_exempt
@require_http_methods(["POST"])
def log_search_result(request):
    '''
    Grava o log de uma consulta. Atualmente o log da consulta já está sendo
    gravado junto do método search da API. Mas ele está exposto aqui para o
    caso dessa dinâmica mudar e ser necessário chamar o método explicitamente.
    '''

    response = LogBusca().save(dict(
        id_sessao=request.POST['id_sessao'],
        id_consulta=request.POST['id_consulta'],
        id_usuario=request.POST['id_usuario'],
        text_consulta=request.POST['text_consulta'],
        algoritmo=request.POST['algoritmo'],
        data_hora=request.POST['data_hora'],
        tempo_resposta=request.POST['tempo_resposta'],
        pagina=request.POST['pagina'],
        resultados_por_pagina=request.POST['resultados_por_pagina'],
        documentos=request.POST['documentos']
    ))

    if len(response[1]) == 0:
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})


@csrf_exempt
@require_http_methods(["POST"])
def log_search_result_click(request):
    '''
    Grava no log o item do ranking clicado pelo usuário.
    '''

    response = LogSearchClick().save(dict(
        id_documento=request.POST['item_id'],
        id_consulta=request.POST['qid'],
        posicao=request.POST['rank_number'],
        tipo_documento=request.POST['item_type'],
        pagina=request.POST['page'],
        timestamp=int(time.time() * 1000),
    ))

    if len(response[1]) == 0:
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})


@csrf_exempt
@require_http_methods(["POST"])
def log_query_suggestion(request):
    query = request.POST['query']
    suggestions = []
    for i in range(5):
        suggestions.append({'label': 'sugestão de consulta '+str(i+1),
                            'value': 'sugestão de consulta '+str(i+1), 'rank_number': i+1, 'suggestion_id': i+1})

    data = {
        'suggestions': suggestions
    }
    return JsonResponse(data)


@csrf_exempt
@require_http_methods(["POST"])
def log_query_suggestion_click(request):
    session_id = request.POST['session_id']
    user_id = request.POST['user_id']
    rank_number = request.POST['rank_number']
    suggestion_id = request.POST['suggestion_id']
    print('[LOG SUGGESTION CLICK] session_id: {:s}, user_id: {:s}, suggestion_id: {:s}, rank_number: {:s}'.format(
        session_id, user_id, suggestion_id, rank_number))
    data = {}
    return JsonResponse(data)


@require_http_methods(["GET"])
def get_log_buscas(request):
    user_id = request.GET.get('user_id',  None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    page = request.GET.get('page', 1)

    if user_id == None and start_date == None and end_date == None:
        response = "Error: At least one parameter must be given."
        return JsonResponse({"response": response})

    log_list = LogBusca.get_list_filtered(
        user_id=user_id, start_date=start_date, end_date=end_date, page=page)

    response = {
        "data": log_list
    }

    return JsonResponse(response)


@require_http_methods(["GET"])
def get_log_clicks(request):
    id_consultas = request.GET.getlist('id_consultas', None)  # list of id_consulta
    
    log_list = LogSearchClick.get_list_filtered(id_consultas=id_consultas)

    response = {
        "data": log_list
    }

    return JsonResponse(response)


@require_http_methods(["GET"])
def generate_log_data(request):
    MAX_USERS = 10
    MAX_QUERIES_PER_DAY = 50
    POSSIBLE_QUERIES = ['Belo Horizonte', 'Uberlândia', 'Contagem', 'Juiz de Fora', 'Betim', 'Montes Claros', 'Ribeirão das Neves', 'Uberaba', 'Governador Valadares', 'Ipatinga', 'Sete Lagoas', 'Divinópolis', 'Santa Luzia', 'Ibirité', 'Poços de Caldas', 'Patos de Minas', 'Pouso Alegre', 'Teófilo Otoni', 'Barbacena', 'Sabará', 'Varginha', 'Conselheiro Lafaiete', 'Vespasiano', 'Itabira', 'Araguari', 'Ubá', 'Passos', 'Coronel Fabriciano', 'Muriaé', 'Araxá', 'Ituiutaba', 'Lavras', 'Nova Serrana', 'Itajubá', 'Nova Lima', 'Pará de Minas', 'Itaúna', 'Paracatu', 'Caratinga', 'Patrocínio', 'Manhuaçu', 'São João del Rei', 'Timóteo', 'Unaí', 'Curvelo', 'Alfenas', 'João Monlevade', 'Três Corações', 'Viçosa', 'Cataguases', 'Ouro Preto', 'Janaúba', 'São Sebastião do Paraíso', 'Esmeraldas', 'Januária', 'Formiga', 'Lagoa Santa', 'Pedro Leopoldo', 'Mariana', 'Ponte Nova', 'Frutal', 'Três Pontas', 'Pirapora', 'São Francisco', 'Congonhas', 'Campo Belo', 'Leopoldina', 'Lagoa da Prata', 'Guaxupé', 'Itabirito', 'Bom Despacho', 'Bocaiúva', 'Monte Carmelo', 'Diamantina', 'João Pinheiro', 'Santos Dumont', 'São Lourenço', 'Caeté', 'Santa Rita do Sapucaí', 'Igarapé', 'Visconde do Rio Branco', 'Machado', 'Almenara', 'Oliveira', 'Salinas', 'Andradas', 'Nanuque', 'Boa Esperança', 'Brumadinho', 'Arcos', 'Ouro Branco', 'Várzea da Palma', 'Iturama', 'Jaíba', 'Porteirinha', 'Matozinhos', 'Capelinha', 'Araçuaí', 'Extrema', 'São Gotardo',]
    start_date = datetime.strptime(request.GET['start_date'], '%d/%m/%Y')
    end_date = datetime.strptime(request.GET['end_date'], '%d/%m/%Y')
    document = Document()

    # num_days = (start_date - end_date).days
    current_date = start_date
    while current_date < end_date:
        current_timestamp = int(datetime(year=current_date.year, month=current_date.month, day=current_date.day).timestamp() * 1000)
        
        # queries of the day
        num_queries = random.randrange(MAX_QUERIES_PER_DAY)
        day_queries = random.sample(POSSIBLE_QUERIES, num_queries)

        # probability of user click in that day
        click_prob = 10 - random.randrange(4)

        # add some random weird queries (to make sure we dont get results)
        num_weird_queries = int(num_queries * random.random()) # the number is based on the number of normal queries
        num_words = random.randrange(2) + 1 # up to 3 words
        for q in range(num_weird_queries):
            weird_query = []
            for w in range(num_words+1):
                word_length = random.randrange(6) + 4 # from 4 to 10 words' length
                letters = string.ascii_lowercase
                weird_query.append(''.join(random.choice(letters) for i in range(word_length)))
            weird_query = ' '.join(weird_query)
            day_queries.append(weird_query)
        # shuffle normal and weird queries
        random.shuffle(day_queries)

        
        print(current_date, num_queries, click_prob)

        # execute queries
        for q in day_queries:
            start = time.time()

            sid = random.getrandbits(128)
            id_usuario = random.randrange(MAX_USERS)+1

            query_timestamp = current_timestamp + random.randrange(60*60*23)*1000, # add some hours and minutes
            query_timestamp = query_timestamp[0] # I dont know why, the operation above returns a tuple

            qid = hashlib.sha1()
            qid.update(bytes(str(query_timestamp) + str(id_usuario) + q + str(sid), encoding='utf-8'))
            qid = qid.hexdigest()

            try:
                total_docs, total_pages, documents, took = document.search(q, 1)
            except:
                print('ERRO:', current_date, q)
                continue
            
            LogBusca().save(dict(
                id_sessao = sid, 
                id_consulta = qid,
                id_usuario = id_usuario,
                text_consulta = q,
                algoritmo = 'BM25',
                data_hora = query_timestamp,
                tempo_resposta = took,
                documentos = [ i.id for i in sorted(documents, key = lambda x: x.rank_number) ],
                pagina = 1,
                resultados_por_pagina = 10,
                tempo_resposta_total = time.time() - start
            ))

            # result click
            if len(documents) > 0:
                # clicked = random.choices([True, False], [click_prob, 1])
                # clicked = clicked[0]
                clicked = random.choice([True, False])
                if clicked:
                    clicked_doc = random.sample(documents, 1)
                    clicked_doc = clicked_doc[0]

                    LogSearchClick().save(dict(
                        id_documento=clicked_doc.id,
                        id_consulta=qid,
                        posicao=clicked_doc.rank_number,
                        tipo_documento=clicked_doc.type,
                        pagina=1,
                        timestamp=(query_timestamp + random.randrange(60)*1000) # up to one minute to click in the result
                    ))
            
            print(qid, q, len(documents)==0, clicked)
        
        current_date = current_date + timedelta(days=1)


    return JsonResponse({'response': 'ok'})

