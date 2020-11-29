import re

import pymorphy2
from nltk import RegexpTokenizer
# import jamspell


class TextProcessor:
    def __init__(self, use_spell_checker=False):
        self.sentence_regex = re.compile(r'(\.|;|!|\?|\.\.\.|…|,|«|»|№|-|\b[0-9]+\b)')
        self.word_tokenizer = RegexpTokenizer(r'\w+')
        self.morph = pymorphy2.MorphAnalyzer()

        self.oni = self.morph.parse('они')[0]
        self.on = self.morph.parse('он')[0]
        self.ona = self.morph.parse('она')[0]

        # после этих слов наречения получают Н: без меня - без него/нее
        self.prepositions = ['без', 'в', 'для', 'до', 'за', 'из', 'к', 'на', 'над',
                             'о', 'от', 'по', 'под', 'перед', 'при', 'про', 'с', 'у',
                             'через', 'возле', 'вокруг', 'впереди', 'мимо', 'напротив',
                             'около', 'после', 'посреди', 'сзади']

        # эти предлоги меняются при изменеии лица: ко мне - к нему/ней
        self.prepositions_variation = ['во', 'ко', 'надо', 'обо', 'подо', 'передо', 'со']

        self.corrector = None
        # if use_spell_checker:
            # self.corrector = jamspell.TSpellCorrector()
            # self.corrector.LoadLangModel('ru.bin')

    def process_preposition(self, preposition, pronoun):
        if preposition in self.prepositions_variation:
            return preposition[:-1], 'н' + pronoun
        if preposition in self.prepositions:
            return preposition, 'н' + pronoun
        return preposition, pronoun

    @staticmethod
    def get_gender(text):
        female_pronoun_with_verb = re.compile(r'(я|Я)\s(не\s)?[а-я]+ла(сь)?')
        remove_all_in_quotes = re.compile(r'«[^»]*»')

        processed_text = remove_all_in_quotes.sub('', text)

        if female_pronoun_with_verb.search(processed_text):
            return 'female'
        return 'male'

    @staticmethod
    def assemble_result_string(sentence_list):
        result_string = ''
        for text in sentence_list:
            if re.match(r'(\.|;|!|\?|\.\.\.|…|,|»)', text):
                result_string += text + ' '
            elif re.match(r'([«])', text):
                result_string += ' ' + text
            elif re.match(r'([0-9]+|№)', text):
                result_string += ' ' + text + ' '
            else:
                result_string += text

        result_string = re.sub(r' {2}', r' ', result_string)
        result_string = re.sub(r'(») \. ([0-9А-Яа-я])', r'\1. \2', result_string)
        result_string = re.sub(r'([А-Я])\. ([А-Я])\.', r'\1.\2.', result_string)
        result_string = re.sub(r'([0-9]) \. ([0-9])', r'\1.\2', result_string)
        result_string = re.sub(r'([0-9]) \. ([А-Я])', r'\1. \2', result_string)
        result_string = re.sub(r'([а-я])s\.s([а-яА-Я])\.', r'\1. \2', result_string)
        result_string = re.sub(r'(.) , (.)', r'\1, \2', result_string)
        result_string = re.sub(r'(.) - (.)', r'\1-\2', result_string)
        result_string = result_string.replace(' . ', '. ')
        return result_string

    def process(self, text_in_first_person):
        gender = self.get_gender(text_in_first_person)

        line = text_in_first_person.strip()
        sentences = self.sentence_regex.split(line)

        processed_sentences = []

        text_in_quotes = False

        for sentence in sentences:
            if self.sentence_regex.match(sentence):
                if sentence == '«':
                    text_in_quotes = True
                if sentence == '»':
                    text_in_quotes = False
                processed_sentences.append(sentence)
                continue

            if text_in_quotes:
                processed_sentences.append(sentence)
                continue

            words = self.word_tokenizer.tokenize(sentence)
            processed_sentence = []

            for i, word in enumerate(words):
                parsed_word = self.morph.parse(word)[0]
                if '1per' in parsed_word.tag or parsed_word.normal_form in ['наш', 'мой']:

                    if parsed_word.normal_form == 'мой':
                        if gender == 'male':
                            processed_word = 'его'
                        else:
                            processed_word = 'eё'

                    if parsed_word.normal_form == 'наш':
                        processed_word = 'их'

                    if 'VERB' in parsed_word.tag:
                        processed_word = parsed_word.inflect({'3per'}).word

                    if 'NPRO' in parsed_word.tag and 'Anph' not in parsed_word.tag:
                        updated_tag = parsed_word.tag.updated_grammemes({'3per', 'Anph'})

                        if parsed_word.normal_form == 'мы':
                            processed_word = self.oni.inflect(updated_tag).word
                        else:
                            if gender == 'male':
                                processed_word = self.on.inflect(updated_tag).word
                            else:
                                processed_word = self.ona.inflect(updated_tag).word

                        if i != 0 and words[i - 1] in self.prepositions + self.prepositions_variation:
                            preposition, pronoun = self.process_preposition(words[i - 1], processed_word)
                            processed_word = pronoun
                            processed_sentence.pop()
                            processed_sentence.append(preposition)

                    processed_sentence.append(processed_word)
                else:
                    if self.corrector:
                        word = self.corrector.FixFragment(word)

                    processed_sentence.append(word)

            processed_sentences.append(' '.join(processed_sentence))

        processed_sentences = [sentence for sentence in processed_sentences if sentence != '']
        result_string = self.assemble_result_string(processed_sentences)
        return result_string


if __name__ == '__main__':

    # example = 'По существу заданных вопросов могу пояснить, что по вышеуказанному адресу я проживаю с родителями Совуновой Аллой Николаевной и ' \
    #           'Совуновым Вадимом Евгеньевичем. В свободное от обучения в средней общеобразовательной школе № 96 время ' \
    #           'я занималась в цирковой студии «Престиж», с которой периодически выступаю, в том числе с выездом. Так, 11.05.2015 ' \
    #           'года я с напарником по цирковой студии Галич Денисом Юрьевичем ' \
    #           'поехали в г. Челябинск на выступление в ледовой арене «Трактор». ' \
    #           '19.05.2015 года я с Галич Д.Ю. возвращались обратно ' \
    #           'в г. Омск, для чего на станции Челябинск мы осуществили ' \
    #           'посадку в пассажирский поезд № 098 сообщением «Кисловодск-Тында» в вагон № 14 на ' \
    #           'места № 22, 24, 26. На одном месте находился реквизит. «Я сказал, отойди от меня». Она подошла ко мне без меня из меня у меня'

    # example = 'Так, 11.05.2015 года я с напарником по цирковой студии Галич Денисом Юрьевичем ' \
    #           'поехали в г. Челябинск на выступление в ледовой арене «Трактор». 19.05.2015 года я с Галич Д.Ю. ' \
    #           'возвращались обратно в г. Омск, для чего на станции Челябинск мы осуществили ' \
    #           'посадку в пассажирский поезд № 098 сообщением «Кисловодск-Тында» в вагон № 14 на ' \
    #           'места № 22, 24, 26. На одном месте находился реквизит. Осуществив посадку и заняв свои ' \
    #           'места мы легли спать, телефон был все время при мне, однако перед тем как лечь спать он ' \
    #           'выключился, т.к. сел заряд аккумулятора. Проснувшись утром по станции Петропавловск ' \
    #           'мы находились на своих местах, так как в вагоне работали пограничники, проводили проверку  ' \
    #           'пассажиров. В вагоне было много пассажиров, некоторые из них в пути следования ' \
    #           'распивали спиртные напитки. В том числе в вагоне из числа пассажиров были военнослужащие, ' \
    #           'других отличительных признаков я не запомнила.'

    example = 'После того как проводник прошел по вагону и предупредил, что до станции Омск оставалось ' \
              'около 15 минут, я решила ' \
              'пойти поставить свой мобильный телефон на зарядку для того, чтобы позвонить маме и ' \
              'сказать о прибытии поезда. Так, я прошла в нерабочий тамбур, где напротив туалета над ' \
              'окном поставила свой мобильный телефон заряжаться, положив его на верхний уступ окна. ' \
              'В момент, когда я ставила телефон на зарядку, в тамбуре напротив туалета стоял проводник вагона, ' \
              'он видел все мои действия. Проводник дожидался пассажира, который находился в туалете, для того чтобы ' \
              'закрыть туалет перед прибытием на станцию Омск. Поставив телефон на зарядку я решила вернуться на свое ' \
              'место, через минуту за мной вышел из ' \
              'тамбура и проводник и прошел к себе. Я находилась на свое месте около 7-10 минут, после ' \
              'чего решила проверить свой мобильный телефон. Также у меня вызвала подозрение женщина, на вид цыганка, ' \
              'которая прошла в сторону туалета. Так, подойдя к нерабочему тамбуру я увидела, что в розетке осталось ' \
              'только зарядное устройство от моего мобильного телефона, самого телефона не было. Я сразу поняла, ' \
              'что его похитили и пошла к проводнику, сообщила о случившемся, на что проводник ответил что по ' \
              'станции Омск вызовет сотрудников полиции для разбирательств.'

    text_processor = TextProcessor()
    result = text_processor.process(example)

    print('\n-------- Исходный текст:\n', example)
    print('\n-------- Обработанный текст:\n', result)
