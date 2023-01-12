def create(db):
    for function_name, function in list(globals().items()):
        if callable(function) and function_name.startswith('create_'):
            function(db)


def create_account_init(db):
    from main.models.account import AccountModel

    AccountModel.query.delete()
    db.session.commit()
    db.session.add(AccountModel(email='*@bot-it.ai'))
    db.session.commit()
