from src.database import delete_debtor_by_cpf

if __name__ == '__main__':
    cpf = '45578760805'
    deleted = delete_debtor_by_cpf(cpf)
    if deleted:
        print(f'Deleted debtor id: {deleted}')
    else:
        print('No debtor found with CPF:', cpf)
