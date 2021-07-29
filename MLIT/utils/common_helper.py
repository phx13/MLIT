class CommonHelper:
    @staticmethod
    def replace_text(from_strs, to_str, text):
        for string in from_strs:
            text = text.replace(string, to_str)
        return text
