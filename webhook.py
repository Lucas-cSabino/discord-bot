import requests

def notificar_discord(mensagem):
    # URL do webhook gerado no Discord
    webhook_url = "https://discord.com/api/webhooks/1316494230310617139/DoAnPPLaxoPBN9ArhtjejT0QpYKSKX03HYgbWRn2FtlHR3KTlj_xLbKhgFfEyWe5Ni7Z"
    # webhook_url = "https://discord.com/api/webhooks/1316193510218797107/8UlWehEavCC2jQQHgC-rpHlVxe_IloxYmUM-9eXBOIg3ygMw-2jEVc8eYXM-2K2ApbHN"

    # Conteúdo da mensagem
    payload = {
        "embeds": [
            {
                "title": "Banco de Dados Travado",
                "description": "O banco de dados do cliente **Supermercado X** travou.",
                "color": 15158332,  # Cor do embed (vermelho)
                "fields": [
                    {"name": "Cliente", "value": "Supermercado X", "inline": True},
                    {"name": "Status", "value": "Travado", "inline": True},
                ]
            }
        ]
    }
    response = requests.post(webhook_url, json=payload)
        
    # Verificar o resultado
    if response.status_code == 204:
        print("Mensagem enviada com sucesso ao Discord!")
    else:
        print(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")

# Exemplo de uso
notificar_discord("⚠️ Banco de dados travado no cliente X!")
