import os
import copy
from datetime import date

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

import PyPDF2
# esses dados são provisórios, pois será fornecido pelo sistema
from payment_voucher_creator.core.database.reader import Reader


class PaymentVoucher():

    def create_payment_voucher(self, file_name, data) -> object:

        # Encontrando a raiz do projeto
        PROJECT_FILE = os.path.dirname(
            os.path.abspath("__file__")).replace("\\", "/")

        # Path do PDF temporário com as tabelas
        PATH_TEMP_FILE = PROJECT_FILE + \
            "/payment_voucher_creator/core/src/pdf/temp/" + file_name + ".pdf"
        # Path do PDF de comprovante de pagamento
        VOUCHERS_PATH = PROJECT_FILE + "/media/pdf/vouchers/"

        def create_tables_pdf():
            # Criando o caminho do arquivo temporário

            def create_paragraph(payment_data: str, color: str = "black", size: str = 10, left_indent: int = 0) -> Paragraph:
                """
                    Recebe uma string como descrição, string para cor e string para o tamanho.
                    Cria um parágrafo personalizado da descrição do pagamento para que haja se necessário quebra de linha
                """
                #! Analisar a formatação do estilo do parágrafo
                current_style = ParagraphStyle(
                    "current_style",
                    aligment=1,
                    leftIndent=left_indent,
                    bulletAnchor="end",
                    fontSize=10,
                    textColor=color
                )
                if not payment_data:
                    payment_data = 0

                # P = Paragraph(
                #     f'''<font size={size} color={color}>{payment_data}</font>''', current_style)
                P = Paragraph(
                    f'''{payment_data}''', current_style)
                return P

            def create_table(payment_data: list[tuple]) -> Table:
                """
                    Recebe uma lista de tuplas.\n
                    Cria uma tabela com essas colunas como header:\n
                    ["DATA", "ID ROTA", "DESCRIÇÃO", "PLACA", "TIPO TRANSAÇÃO",
                    "ACRÉS.", "VALOR", "VALOR\nPARADAS", "ADIC.", "TOTAL", "STATUS"]
                """

                def setting_style_table_by_payment_data(payment_data: list[tuple]) -> list[tuple]:
                    """
                    Essa função analisa quantas linhas de descontos tem e as colore de vermelho
                    """
                    lines_to_formatter = []
                    for index, pay_data in enumerate(payment_data):
                        if pay_data[4] == "DESCONTO":
                            lines_to_formatter.append(index + 1)

                    cells_style = [("TEXTCOLOR", (4, line), (7, line),
                                    colors.red) for line in lines_to_formatter]

                    return cells_style

                # Largura desejada da tabela
                tabela_largura_desejada = 850

                # Criar dados para a tabela
                headers = ["DATA", "ID ROTA", "DESCRIÇÃO", "PLACA",
                           "TIPO\nTRANSAÇÃO", "VALOR", "ADIC.", "TOTAL", "STATUS"]

                # Criar uma tabela com largura pré-definida
                style = getSampleStyleSheet()["BodyText"]
                style_cell = ParagraphStyle(
                    "cell",
                    parent=style,
                    alignment=1,  # Centralizar texto na célula,
                    valign=1,
                    spaceAfter=6,
                    wordWrap='CJK',
                    fontSize=10
                )
                table_data = [headers] + payment_data
                col_widths = [tabela_largura_desejada /
                              len(headers)] * len(headers)
                col_widths[0] = 54  # nqoa Date
                col_widths[1] = 77  # nqoa Route number
                col_widths[2] = 347  # nqoa Description
                col_widths[3] = 50  # nqoa License plate
                col_widths[4] = 70  # nqoa Transaction type
                col_widths[5] = 60  # nqoa Value
                col_widths[6] = 60  # nqoa Additional
                col_widths[7] = 60  # nqoa Total
                col_widths[8] = 65  # nqoa Status
                table = Table(table_data, colWidths=col_widths)

                #! CRIAR UMA FUNÇÃO QUE ANALISA AS LINHAS QUE TEM DESCONTO E CONFIGURA O ESTILHO DA TABELA PARA MUDAR O ESTILO DE ALGUMAS CÉLULAS ESPECÍFICAS PARA CONSEGUIR MANTER O ALINHAMENTO

                # Estilo da tabela
                style_table_tuple = [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),   # noqa Centraliza horizontalmente
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # noqa Centraliza verticalmente
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ('CELL', (0, 0), (-1, -1), 'LEFT', style_cell),
                    ('CELL', (0, 1), (1, -1), 'LEFT', style_cell),
                    ('ROWHEIGHT', (0, 0), (0, 0), 10),
                    ('COLWIDTH', (1, 0), (1, -1), 200),
                    ("SIZE", (0, 0), (-1, -1), 10),
                ]
                style_table_extra = setting_style_table_by_payment_data(
                    payment_data)
                if style_table_extra:
                    style_table_tuple.extend(
                        style_table_extra)

                style_table = TableStyle(style_table_tuple)
                table.setStyle(style_table)

                return table

            def transform_data(data_list: list[dict]) -> list[dict]:
                transformed_Data = []
                # for payment_data in data_list:
                #     if payment_data['transactionType'] != "DESCONTO":
                #         payment_data = (payment_data['routeDate'],
                #                         payment_data['idRoute'],
                #                         create_paragraph(
                #                             payment_data['description']),
                #                         payment_data['licensePlate'],
                #                         payment_data['transactionType'],
                #                         payment_data['value'],
                #                         payment_data['additional'],
                #                         payment_data['total'],
                #                         payment_data['paymentStatus'])
                #     else:
                #         payment_data = (payment_data['routeDate'],
                #                         payment_data['idRoute'],
                #                         create_paragraph(
                #                             payment_data['description'], "red"),
                #                         payment_data['licensePlate'],
                #                         payment_data['transactionType'],
                #                         create_paragraph(
                #                             payment_data['value'], "red", left_indent=10),
                #                         create_paragraph(
                #                             payment_data['additional'], "red", left_indent=10),
                #                         create_paragraph(
                #                             payment_data['total'], "red", left_indent=10),
                #                         payment_data['paymentStatus'])
                #     transformed_Data.append(payment_data)
                for payment_data in data_list:
                    if payment_data['transactionType'] != "DESCONTO":
                        payment_data = (payment_data['routeDate'],
                                        payment_data['idRoute'],
                                        create_paragraph(
                                            payment_data['description']),
                                        payment_data['licensePlate'],
                                        payment_data['transactionType'],
                                        payment_data['value'],
                                        payment_data['additional'],
                                        payment_data['total'],
                                        payment_data['paymentStatus'])
                    else:
                        payment_data = (payment_data['routeDate'],
                                        payment_data['idRoute'],
                                        create_paragraph(
                                            payment_data['description'], "red"),
                                        payment_data['licensePlate'],
                                        payment_data['transactionType'],
                                        payment_data['value'],
                                        payment_data['additional'],
                                        payment_data['total'],
                                        payment_data['paymentStatus'])
                    transformed_Data.append(payment_data)

                return transformed_Data

            def create_tables(payment_data):
                """
                Cria uma tabela com no máximo 375 pontos de altura/height, se devido a quantidade de dados a tabela ficar maior que 375 pontos, irá solicitar a criação de uma nova tabela com os dados faltantes e assim sucessivamente.
                """
                # Variável auxiliar para armazenar as linhas de pagamento que serão usadas para compor a tabela da vez
                aux_list = []
                # Variável para identificar se a criação da tabela foi parada pelo seu tamanho
                blocked = False
                for index in range(len(payment_data), 0, -1):
                    aux_list.append(payment_data[index - 1])

                    # Passar 0, 0 para indicar que não há restrições de largura e altura
                    table_size = create_table(aux_list).wrap(0, 0)

                    # ! PARA ÚLTIMA PÁGINA A TABELA DEVERÁ TER NO MÁXIMO 365 PONTOS
                    # ! PARA AS DEMAIS 375 PONTOS

                    if table_size[1] <= 365:
                        # Se a tabela rompeu o limite, irá retirar a última adição para que a tabela fique abaixo do tamanho máximo
                        payment_data.pop()
                        continue
                    aux_list.pop()
                    blocked = True

                    # Criar uma nova página aqui
                    break

                tables.append(create_table(aux_list))
                if blocked:
                    # Se o looping foi parado por seu tamanho, irá chamar a função novamente até criar todas as tabelas necessárias
                    create_tables(payment_data_formated)

            def create_pdf_with_tables(path_file: str, contents: list[Table]):
                # Criar um objeto canvas

                canva_pdf = canvas.Canvas(path_file, pagesize=landscape(A4))

                for index in range(0, (len(contents))):

                    # Adicionar conteúdo à primeira página
                    width, height = landscape(A4)
                    dimensions = contents[index].wrapOn(
                        canva_pdf, width, height)
                    # Calculando o tamanho da tabela para que ela sempre fique no topo da página
                    # O cáculo é o tamanho da página menos o tamanho total que a tabela precisa para ocupar o espaço necessário no canva

                    #! Inserindo as informações do colaborador na página antes de inserir a tabela
                    if index != (len(contents) - 1):
                        insert_informations_on_the_page(
                            data, canva_pdf, False)
                    else:
                        insert_informations_on_the_page(
                            data, canva_pdf, True)

                    # * Configurando onde a tabela vai ser inserida na tabela
                    contents[index].drawOn(
                        canva_pdf, 0, (height - dimensions[1]) - 180)
                    # Adicionar nova página
                    canva_pdf.drawString(780, 10, f"Página {index + 1}")
                    canva_pdf.showPage()

                    #! Dependendo da quantidade de conteúdos, adicionar uma nova página
                # Salvar o PDF
                canva_pdf.save()

            # Variável que armazena as tabelas que estão sendo geradas
            tables = []

            payment_data_formated = transform_data(data["paymentData"])
            create_tables(payment_data_formated)

            # Substitua 'exemplo.pdf' pelo nome desejado para o arquivo
            create_pdf_with_tables(PATH_TEMP_FILE, tables)

        def insert_informations_on_the_page(data: dict[str | list], page: canvas.Canvas, totals: bool) -> None:
            font_name = "Helvetica"
            font_size = 12
            # Define a fonte do texto
            page.setFont(font_name, font_size)
            # Inserir todos os dados do colaborador
            # *  ID and name
            page.drawString(
                40, 460, name_formatter(str(data["employeeInformation"]["id"]), data["employeeInformation"]["name"]))

            # * CPF
            page.drawString(40, 445, f"CPF: {
                            data["employeeInformation"]["cpf"] if data["employeeInformation"]["cpf"] else ""}")
            # * Service center
            page.drawString(40, 430, f"Service center: {
                            data["employeeInformation"]["serviceCenter"]}")
            # * Period
            page.drawString(365, 460, f"PERÍODO: {data["period"]}")
            # * Phone number
            page.drawString(365, 445, f"Celular: {
                            data["employeeInformation"]["phoneNumber"] if data["employeeInformation"]["phoneNumber"] else ""}")
            # * Pix key
            page.drawString(365, 430, f"Chave pix: {
                            data["employeeInformation"]["bankData"]["pixKey"] if data["employeeInformation"]["bankData"]["pixKey"] else ""}")
            # * Bank name
            page.drawString(690, 460, f"Banco: {
                            data["employeeInformation"]["bankData"]["name"] if data["employeeInformation"]["bankData"]["name"] else ""}")
            # * Bank agency
            page.drawString(690, 445, f"Agência: {
                            data["employeeInformation"]["bankData"]["agency"] if data["employeeInformation"]["bankData"]["agency"] else ""}")
            # * Bank account
            page.drawString(690, 430, f"Conta: {
                            data["employeeInformation"]["bankData"]["account"] if data["employeeInformation"]["bankData"]["account"] else ""}")
            # * Created at
            page.setFont("Helvetica", 9)
            page.drawString(178, 16, f"{data["createdAt"]}")
            # * Created at
            page.drawString(705, 16, f"{data["userName"]}")

            if totals == True:
                # ? Se a página for a de totais, então serão adicionados os valores de totais

                # Cáculo do tamanho das Strings para elas ficarem centralizadas no meio dos totais:
                grossValueStrWidth = page.stringWidth(
                    data["paymentTotals"]["grossValue"], font_name, font_size)
                fullDiscountStrWidth = page.stringWidth(
                    data["paymentTotals"]["fullDiscount"], font_name, font_size)
                totalValueStrWidth = page.stringWidth(
                    data["paymentTotals"]["totalValue"], font_name, font_size)
                pendingValueStrWidth = page.stringWidth(
                    data["paymentTotals"]["pendingValue"], font_name, font_size)
                payableStrWidth = page.stringWidth(
                    data["paymentTotals"]["payable"], font_name, font_size)

                # * Gross value
                page.drawString(115 - (grossValueStrWidth / 2), 32,
                                data["paymentTotals"]["grossValue"])
                # * Full discount
                page.drawString(275 - (fullDiscountStrWidth / 2), 32,
                                data["paymentTotals"]["fullDiscount"])
                # * Total value
                page.drawString(440 - (totalValueStrWidth / 2), 32,
                                data["paymentTotals"]["totalValue"])
                # * Pending value
                page.drawString(593 - (pendingValueStrWidth / 2), 32,
                                data["paymentTotals"]["pendingValue"])
                # * Payable
                page.drawString(745 - (payableStrWidth / 2), 32,
                                data["paymentTotals"]["payable"])

        def crop_tables_and_add_informations(pdf_tabelas_path, voucher_name, data):
            base_pdf_canva = PROJECT_FILE + \
                "/payment_voucher_creator/core/resources/canvas/PAYMENT-INVOICE-CANVAS.pdf"
            base_pdf_canva_totals = PROJECT_FILE + \
                "/payment_voucher_creator/core/resources/canvas/PAYMENT-INVOICE-CANVAS-TOTALS.pdf"

            # Abre os arquivos PDF de origem e destino
            with open(pdf_tabelas_path, 'rb') as pdf_tabelas_binario, open(base_pdf_canva, 'rb') as base_pdf_canva_binario, open(base_pdf_canva_totals, 'rb') as base_pdf_canva_totals_binario:
                # Cria objetos PDF

                # Obtendo o PDF das tabelas
                pdf_tables_reader = PyPDF2.PdfReader(pdf_tabelas_binario)
                # Obtendo o PDF da base canva
                pdf_base_canva_reader = PyPDF2.PdfReader(
                    base_pdf_canva_binario)
                # Obtendo o PDF da base canva totals
                pdf_base_canva__totals_reader = PyPDF2.PdfReader(
                    base_pdf_canva_totals_binario)
                # Obtendo a quantidade de páginas, assim obtendo a quantidade de tabelas
                num_pages_pdf_tables = len(pdf_tables_reader.pages)

                payment_voucher = PyPDF2.PdfWriter()

                # Cria a quantidade de páginas necessárias para as tabelas
                # transformation = PyPDF2.Transformation().translate(tx=0, ty=-180)
                for i in range(0, num_pages_pdf_tables):

                    # Pegar a página base canva do PAYMENT-INVOICE-CANVA como cópia para não interferir nas outras páninas
                    base_canva_page = None
                    if i != (num_pages_pdf_tables - 1):
                        base_canva_page = copy.copy(
                            pdf_base_canva_reader.pages[0])
                    else:
                        base_canva_page = copy.copy(
                            pdf_base_canva__totals_reader.pages[0])

                    # Adicionando um transformation para a tabela descer 100 pontos e ocupar o lugar correto na página
                    # pdf_tables_reader.pages[i].add_transformation(
                    #     transformation)

                    # Juntando a página base com a tabela
                    base_canva_page.merge_page(pdf_tables_reader.pages[i])

                    # Adicionando a página de comprovante de pagamento ao arquivo
                    payment_voucher.add_page(base_canva_page)

                with open(VOUCHERS_PATH + voucher_name, 'wb') as arquivo_destino_atualizado:
                    payment_voucher.write(arquivo_destino_atualizado)

                    return VOUCHERS_PATH + voucher_name

        def name_formatter(id: str, name: str) -> str:
            """
                Essa função recebe o ID e o nome do colaborador faz a contagem da quantidade de caracteres e se ela for maior a 44, retorna o nome do colaborador abreviado
            """
            name_length = len(
                f"ID {id} - {name}")

            name_formatted = name

            if name_length > 44:
                words = name.split()

                # Add first name
                name_formatted = words[0]

                # Add abbreviated middle name
                for i in range(1, len(words) - 1):
                    if len(words[i]) > 3:
                        name_formatted += f" {words[i][0]}."
                    else:
                        name_formatted += f" {words[i]}"
                # Add last name
                name_formatted += f" {words[-1]}"

            return f"ID {id} - {name_formatted}"

        create_tables_pdf()
        payment_voucher_path = crop_tables_and_add_informations(
            PATH_TEMP_FILE, file_name + ".pdf", data)

        # Excluindo o arquivo de tabelas temporários
        try:
            os.remove(PATH_TEMP_FILE.replace("/", "\\"))
            print(f'O arquivo {PATH_TEMP_FILE.replace(
                "/", "\\")} foi excluído com sucesso.')

            return payment_voucher_path
        except FileNotFoundError:
            print(f'O arquivo {PATH_TEMP_FILE.replace(
                "/", "\\")} não foi encontrado.')
            return payment_voucher_path
        except Exception as e:
            print(f"Ocorreu um erro ao excluir o arquivo: {e}")
            return payment_voucher_path.detach()


if __name__ == '__main__':
    data = {
        "employeeInformation": {
            "id": 10101,
            "name": "Fulano da silva tropeiro teste",
            "serviceCenter": "SSP5",
            "cpf": "010101010101",
            "bankData": {
                "name": "Nubank",
                "agency": "0001",
                "account": "110001",
                "pixKey": "fulano@gmail.com"
            }
        },
        "paymentData": Reader().getPaymentMirrors("202401Q1"),
        "period": "202401Q1",
        "paymentTotals": {
            "grossValue": "1000,00",
            "fullDiscount": "500,00",
            "totalValue": "1000,00",
            "pendingValue": "0,00",
            "payable": "1000,00"
        },
        "user": "Wellington Silva",
        "createdAt": "29/01/2024"
    }

    PaymentVoucher().create_payment_voucher(
        'exemplo-completo', data)
