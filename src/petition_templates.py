"""Templates de Petições Judiciais para Processos de Execução/Cumprimento de Sentença"""

PETITION_TEMPLATES = {
    # Petições para Processo Inicial
    "inicial": {
        "juntada_custas": {
            "name": "Petição de Juntada de Custas",
            "description": "Petição para juntar comprovantes de custas processuais",
            "content": """À Ilustríssima Excelentíssima Autoridade Judicial,

Vem respeitosamente perante Vossa Excelência o(a)
___________________________________, por intermédio de seu advogado e procurador infra
assinado, à luz das disposições da Lei 6.830/1980 (Lei de Execução Fiscal), para REQUERER
a juntada aos autos dos comprovantes de custas processuais necessários para o prosseguimento
desta ação executiva.

Segue em anexo a documentação comprobatória das custas despendidas com a presente execução,
incluindo honorários advocatícios e demais gastos processuais.

Requer-se o recebimento desta petição e a juntada da documentação anexa ao processo, a fim
de que seja considerado para fins de cálculo do crédito executado.

Nestes termos, pede deferimento.

Respectosamente submetido,

Data: ___/___/______
Assinado digitalmente por: ____________________________
OAB nº: _________
"""
        },
        "juntada_procuracao": {
            "name": "Petição de Juntada de Procuração",
            "description": "Petição para juntar documento de procuração ao processo",
            "content": """À Ilustríssima Excelentíssima Autoridade Judicial,

Vem respeitosamente perante Vossa Excelência o(a)
___________________________________, para REQUERER a juntada aos autos da procuração
que confere poderes a este advogado para representá-lo(a) nesta ação.

A procuração segue em anexo, devidamente registrada em cartório, conferindo plenos poderes
ao subscritor desta petição para praticar todos os atos processuais necessários à defesa
dos interesses do outorgante.

Requer-se o recebimento desta petição e a juntada do instrumento de mandato ao processo,
a fim de que conste do feito.

Nestes termos, pede deferimento.

Data: ___/___/______
Assinado digitalmente por: ____________________________
OAB nº: _________
"""
        },
        "busca_enderecos": {
            "name": "Petição de Busca de Endereços",
            "description": "Petição requisitando localização de endereços do devedor",
            "content": """À Ilustríssima Excelentíssima Autoridade Judicial,

Vem respeitosamente perante Vossa Excelência o(a)
___________________________________ requerer a expedição de ofícios aos órgãos públicos
competentes para localização e confirmação dos endereços do devedor
___________________________________________, a fim de possibilitar o cumprimento da
citação e intimação necessárias para o prosseguimento da ação.

Solicita-se, especificamente:

1. Ao Serviço de Proteção ao Crédito (SPC) - localização de endereço cadastrado;
2. À RECEITA FEDERAL - endereço constante do cadastro de contribuintes;
3. À PREFEITURA MUNICIPAL - comprovação de endereço por registros de IPTU;
4. A órgãos públicos que porventura tenham informações sobre localização do devedor.

Ressalva-se que a busca de endereços é medida necessária ao cumprimento da citação,
sendo indispensável para a continuidade do processo.

Nestes termos, pede deferimento.

Data: ___/___/______
Assinado digitalmente por: ____________________________
OAB nº: _________
"""
        },
        "penhora_online": {
            "name": "Petição de Penhora On-line",
            "description": "Petição requisitando bloqueio de valores em contas bancárias",
            "content": """À Ilustríssima Excelentíssima Autoridade Judicial,

Vem respeitosamente perante Vossa Excelência o(a)
___________________________________ requerer a expedição de ofício ao Banco Central do Brasil,
para realização de bloqueio via sistema BACENJUD, visando penhorar valores em conta(s)
corrente(s) ou poupança do devedor ___________________________________________.

Fundamenta-se o presente requerimento:

1. Na urgência da medida, evitando dissipação de patrimônio do devedor;
2. Na eficácia reconhecida do sistema BACENJUD para localização de créditos;
3. Na autorização legal prevista na Lei 11.382/2006 para penhora de valores em instituições
   financeiras;
4. Na necessidade de execução rápida e eficiente da sentença/decisão.

Solicita-se que o ofício seja expedido ao Banco Central com instruções para bloqueio de
valores até o montante da dívida, acrescido de custas e honorários advocatícios.

Nestes termos, pede deferimento.

Data: ___/___/______
Assinado digitalmente por: ____________________________
OAB nº: _________
"""
        }
        ,
        "procura_csv": {
            "name": "Procuração Padrão",
            "description": "Modelo de procuração para outorga de poderes ao advogado",
            "content": """PROCURAÇÃO

    Eu, {{debtor_name}}, portador(a) do CPF/CNPJ n.º {{debtor_cpf_cnpj}}, por este instrumento, nomeio e constituo como meu bastante procurador(a) o(a) advogado(a) {{attorney_name}} - OAB {{attorney_oab}}, para representar-me em juízo e fora dele, com poderes para receber citação, transigir, firmar acordos, substabelecer, e praticar todos os demais atos necessários ao regular andamento do processo.

    Data: {{today}}
    Assinatura: __________________________
    """
        },
    },
    
    # Petições para Cumprimento de Sentença
    "cumprimento": {
        "requisicao_cumprimento": {
            "name": "Requisição de Cumprimento de Sentença",
            "description": "Petição inicial para cumprimento de sentença condenatória",
            "content": """À Ilustríssima Excelentíssima Autoridade Judicial,

Vem respeitosamente perante Vossa Excelência o(a)
___________________________________, por intermédio de seu advogado infra assinado,
requerer o cumprimento da sentença condenatória prolatada neste processo, conforme segue:

DADOS DA SENTENÇA:
- Processo nº: ________________________________
- Data da Sentença: ___/___/______
- Valor Condenado: R$ ____________________
- Credor: ___________________________________
- Devedor: __________________________________

O devedor foi intimado da condenação e não efetuou o pagamento voluntário no prazo legal.
Deste modo, requere-se:

1. A expedição de mandado para citação do devedor e intimar-lhe do cumprimento de sentença;
2. A concessão de prazo de 15 (quinze) dias para pagamento voluntário;
3. Na inércia do devedor, a execução forçada pelos meios legais disponíveis.

Documentação anexa:
- Cópia autenticada da sentença
- Cálculo atualizado da dívida
- Procuração e documentos pessoais

Nestes termos, pede deferimento.

Data: ___/___/______
Assinado digitalmente por: ____________________________
OAB nº: _________
"""
        },
        "penhora_bens": {
            "name": "Petição de Penhora de Bens Móveis/Imóveis",
            "description": "Petição requisitando penhora de bens para satisfação de crédito",
            "content": """À Ilustríssima Excelentíssima Autoridade Judicial,

Vem respeitosamente perante Vossa Excelência o(a)
___________________________________ requerer a penhora de bens do devedor
___________________________________________, a fim de satisfazer o crédito exigível
decorrente de sentença condenatória.

DADOS DA EXECUÇÃO:
- Valor Principal: R$ ____________________
- Juros e Multa: R$ ____________________
- Valor Total: R$ ____________________

BENS PASSÍVEIS DE PENHORA:
1. Imóvel situado em ________________________________________
   Matrícula nº: _________________ Cartório de Registro: _________________
   
2. Veículo(s): _____________________________________________
   Placa(s): _________________ Renavam: _________________
   
3. Valores em instituições financeiras (via BACENJUD)

Solicita-se a expedição de mandado para efetivação da penhora, assim como a nomeação de
depositário e realização de avaliação dos bens, a fim de proceder à sua venda em hasta
pública ou via leilão eletrônico.

Nestes termos, pede deferimento.

Data: ___/___/______
Assinado digitalmente por: ____________________________
OAB nº: _________
"""
        },
        "arresto_bens": {
            "name": "Petição de Arresto Preventivo",
            "description": "Petição para arresto preventivo de bens antes de sentença definitiva",
            "content": """À Ilustríssima Excelentíssima Autoridade Judicial,

Vem respeitosamente perante Vossa Excelência o(a)
___________________________________ requerer o arresto preventivo de bens do devedor
___________________________________________, como medida cautelar necessária para
evitar a dissipação de patrimônio e garantir o cumprimento futuro da obrigação.

FUNDAMENTAÇÃO LEGAL:
1. Lei 11.382/2006 - Penhora de bens antes do trânsito em julgado;
2. Código de Processo Civil - Medidas cautelares satisfativas;
3. Princípio da cautela e da efetividade da prestação jurisdicional.

BENS A ARRESTAR:
Conforme documentação anexa, identificam-se os seguintes bens do devedor:
- Imóvel(is): ___________________________________
- Veículo(is): ___________________________________
- Créditos e valores: ___________________________

Ressalva-se a urgência da medida, ante o risco de frustração do resultado útil do processo,
bem como a capacidade econômica do devedor de prejudicar o crédito.

Nestes termos, pede deferimento.

Data: ___/___/______
Assinado digitalmente por: ____________________________
OAB nº: _________
"""
        },
        "juntada_custas_execucao": {
            "name": "Petição de Juntada de Custas da Execução",
            "description": "Petição para inclusão de custas processuais no valor executado",
            "content": """À Ilustríssima Excelentíssima Autoridade Judicial,

Vem respeitosamente perante Vossa Excelência o(a)
___________________________________ requerer a juntada e computação nos autos de
novo aditamento de custas processuais e honorários advocatícios, decorrentes do cumprimento
de sentença.

CUSTAS A SEREM ADICIONADAS:
- Emolumentos de registro: R$ ____________________
- Custas cartoriais: R$ ____________________
- Honorários advocatícios adicionais: R$ ____________________
- Demais despesas processuais: R$ ____________________
- TOTAL: R$ ____________________

Conforme jurisprudência consolidada, as custas e despesas processuais do cumprimento de
sentença devem ser adicionadas ao débito primitivo, competindo ao devedor seu pagamento.

Segue em anexo documentação comprobatória de todas as despesas relacionadas.

Requer-se a aceitação desta petição e a computação das custas no cálculo da dívida exigível.

Nestes termos, pede deferimento.

Data: ___/___/______
Assinado digitalmente por: ____________________________
OAB nº: _________
"""
        }
        ,
        "procura_csv_exec": {
            "name": "Procuração - Execução",
            "description": "Procuração voltada à fase de cumprimento de sentença",
            "content": """PROCURAÇÃO PARA CUMPRIMENTO DE SENTENÇA

    Eu, {{debtor_name}}, CPF/CNPJ: {{debtor_cpf_cnpj}}, por este instrumento aventureiro, outorgo ao advogado {{attorney_name}} - OAB {{attorney_oab}}, poderes especiais para representar-me na fase de cumprimento de sentença, inclusive para requerer medidas executivas, receber alvarás, firmar termos, substabelecer, negociar e praticar todos os atos necessários.

    Data: {{today}}
    Assinatura: __________________________
    """
        },
        "substabelecimento_exec": {
            "name": "Substabelecimento",
            "description": "Substabelecimento padrão para substabelecer poderes a outro advogado",
            "content": """SUBSTABELECIMENTO

    Eu, {{origin_attorney}} - OAB {{origin_oab}}, substabeleço ao(à) advogado(a) {{dest_attorney}} - OAB {{dest_oab}} os poderes a seguir descritos:

    {{powers}}

    Data: {{today}}
    Assinatura: __________________________
    """
        }
    }
}

def get_templates_for_process_type(process_type):
    """Retorna templates de petições para um tipo de processo específico."""
    return PETITION_TEMPLATES.get(process_type, {})

def get_all_petition_types():
    """Retorna lista de todos os tipos de petição disponíveis."""
    all_types = {}
    for process_type, petitions in PETITION_TEMPLATES.items():
        for petition_id, petition_data in petitions.items():
            all_types[f"{process_type}_{petition_id}"] = petition_data
    return all_types

def get_petition_content(process_type, petition_id):
    """Retorna o conteúdo de uma petição específica."""
    if process_type in PETITION_TEMPLATES and petition_id in PETITION_TEMPLATES[process_type]:
        return PETITION_TEMPLATES[process_type][petition_id]["content"]
    return None


def render_template(template_text: str, context: dict):
    """Renderiza placeholders simples no template substituindo por valores do contexto.

    Suporta placeholders como: {{debtor_name}}, {{debtor_cpf_cnpj}}, {{process_number}},
    {{forum}}, {{vara}}, {{debt_value}}, {{client_name}}, {{today}}.
    Qualquer placeholder não localizado será mantido no texto.
    """
    result = template_text
    if not template_text:
        return ''
    # Flatten keys to simple placeholders
    for key, value in (context or {}).items():
        placeholder = '{{' + key + '}}'
        if value is None:
            value = ''
        result = result.replace(placeholder, str(value))

    # Auto-add common placeholders
    from datetime import datetime
    result = result.replace('{{today}}', datetime.now().strftime('%d/%m/%Y'))
    return result
