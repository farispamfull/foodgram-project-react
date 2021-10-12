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
