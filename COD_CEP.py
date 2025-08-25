import requests
import json
from functools import lru_cache

class CEPService:
    @staticmethod
    @lru_cache(maxsize=1000)
    def buscar_cep(cep):
        """
        Busca informações de endereço com tratamento completo de erros
        Inclui verificação de resposta vazia e JSON inválido
        """
        try:
            # Validação rigorosa do CEP
            cep_limpo = ''.join(filter(str.isdigit, str(cep)))
            if len(cep_limpo) != 8:
                return {
                    'erro': True,
                    'tipo': 'validacao',
                    'mensagem': 'CEP deve conter exatamente 8 dígitos',
                    'cep_original': cep,
                    'cep_limpo': cep_limpo
                }

            # Tentativa com BrasilAPI
            resultado = CEPService._consultar_api(
                f"https://brasilapi.com.br/api/cep/v2/{cep_limpo}",
                "BrasilAPI"
            )
            
            if not resultado['erro']:
                return resultado

            # Fallback para ViaCEP
            return CEPService._consultar_api(
                f"https://viacep.com.br/ws/{cep_limpo}/json/",
                "ViaCEP"
            )

        except Exception as e:
            return {
                'erro': True,
                'tipo': 'inesperado',
                'mensagem': f'Erro inesperado: {str(e)}'
            }

    @staticmethod
    def _consultar_api(url, fonte):
        """Método genérico para consulta de APIs com tratamento robusto"""
        try:
            response = requests.get(url, timeout=10)
            
            # Verificação crítica de resposta vazia
            if not response.text.strip():
                return {
                    'erro': True,
                    'tipo': 'resposta_vazia',
                    'mensagem': f'A {fonte} retornou resposta vazia',
                    'status_code': response.status_code
                }

            # Verificação de JSON válido
            try:
                dados = response.json()
            except json.JSONDecodeError:
                return {
                    'erro': True,
                    'tipo': 'json_invalido',
                    'mensagem': f'Resposta inválida da {fonte}',
                    'resposta_crua': response.text[:100] + '...' if response.text else None
                }

            # Tratamento específico para cada API
            if fonte == "BrasilAPI":
                if response.status_code == 404:
                    return {
                        'erro': True,
                        'tipo': 'nao_encontrado',
                        'mensagem': dados.get('message', 'CEP não encontrado')
                    }
                if response.status_code == 400:
                    return {
                        'erro': True,
                        'tipo': 'validacao_api',
                        'mensagem': 'CEP rejeitado pela API',
                        'detalhes': dados.get('errors', [])
                    }
                
                return {
                    'cep': dados.get('cep', '').replace('-', ''),
                    'logradouro': dados.get('street', ''),
                    'bairro': dados.get('neighborhood', ''),
                    'cidade': dados.get('city', ''),
                    'estado': dados.get('state', ''),
                    'fonte': fonte,
                    'erro': False
                }

            else:  # ViaCEP
                if 'erro' in dados:
                    return {
                        'erro': True,
                        'tipo': 'nao_encontrado',
                        'mensagem': 'CEP não encontrado'
                    }
                
                return {
                    'cep': dados.get('cep', '').replace('-', ''),
                    'logradouro': dados.get('logradouro', ''),
                    'complemento': dados.get('complemento', ''),
                    'bairro': dados.get('bairro', ''),
                    'cidade': dados.get('localidade', ''),
                    'estado': dados.get('uf', ''),
                    'fonte': fonte,
                    'erro': False
                }

        except requests.Timeout:
            return {
                'erro': True,
                'tipo': 'timeout',
                'mensagem': f'Tempo de conexão com {fonte} esgotado'
            }
        except requests.RequestException as e:
            return {
                'erro': True,
                'tipo': 'conexao',
                'mensagem': f'Erro na conexão com {fonte}: {str(e)}'
            }

# Exemplo de uso com tratamento completo:
if __name__ == "__main__":
    ceps_teste = ["01001000", "00000000", "123", "invalido12345", ""]
    
    for cep in ceps_teste:
        print(f"\nConsulta para: {repr(cep)}")
        resultado = CEPService.buscar_cep(cep)
        
        if resultado.get('erro'):
            print(f"ERRO ({resultado['tipo']}): {resultado['mensagem']}")
            if resultado.get('detalhes'):
                for detalhe in resultado['detalhes']:
                    print(f" - {detalhe.get('message')}")
        else:
            print("Endereço encontrado:")
            print(f"{resultado['logradouro']}, {resultado['bairro']}")
            print(f"{resultado['cidade']}/{resultado['estado']}")
            print(f"Fonte: {resultado['fonte']}")