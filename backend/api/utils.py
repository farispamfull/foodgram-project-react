class Util:
    @staticmethod
    def make_shopping_text(ingredients):
        text = []
        for item in ingredients:
            line = (f'{item["ingredients__name"]} '
                    f'{item["ingredients__measurement_unit"]}  '
                    f'{item["total"]}\n')
            text.append(line)
        return text

    @staticmethod
    def normalize_email(email):
        """
        Normalize the email address by lowercasing the domain part of it.
        """

        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = email_name.lower() + '@' + domain_part.lower()
        return email
