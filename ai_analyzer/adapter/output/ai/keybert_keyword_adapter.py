from keybert import KeyBERT
from kiwipiepy import Kiwi  # 추가: 형태소 분석기
from ai_analyzer.application.port.keyword_extraction_port import KeywordExtractionPort


class KeybertKeywordAdapter(KeywordExtractionPort):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            print("Loading KeyBERT & Kiwi model...")

            # 1. KeyBERT 모델 로드
            cls.__instance.kw_model = KeyBERT(model='paraphrase-multilingual-MiniLM-L12-v2')

            # 2. Kiwi 형태소 분석기 로드 (고유명사 추출용)
            cls.__instance.kiwi = Kiwi()

            print("KeyBERT & Kiwi loaded.")
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def extract_keywords(self, text: str, top_n: int = 5) -> list:
        # 1. 형태소 분석을 통해 고유명사(NNP) 후보군 추출
        # 외국어(SL)도 고유명사일 확률이 높으므로 포함하는 것이 좋습니다 (예: Tesla, Apple)
        tokens = self.kiwi.analyze(text)
        candidates = []

        # tokens[0][0]은 분석 결과의 첫 번째 문장/분석 결과를 의미합니다.
        for token in tokens[0][0]:
            # NNP: 고유명사, SL: 외국어
            if token.tag in ['NNP', 'SL']:
                candidates.append(token.form)

        # 중복 제거 (순서 유지를 위해 dict 사용하거나 그냥 set 사용)
        candidates = list(set(candidates))

        # 2. 고유명사 후보가 없을 경우 예외 처리 (빈 리스트 반환 혹은 전체 분석)
        if not candidates:
            return []
            # 또는 아래처럼 기본 추출로 폴백(fallback)할 수도 있습니다.
            # return self._fallback_extraction(text, top_n)

        # 3. KeyBERT에게 전체 텍스트가 아닌 '후보 단어들(candidates)' 중에서만 뽑으라고 시킴
        keywords = self.kw_model.extract_keywords(
            text,
            candidates=candidates,  # 핵심 변경 사항
            keyphrase_ngram_range=(1, 1),
            stop_words=None,
            top_n=top_n
        )

        return [kw[0] for kw in keywords]

    # (옵션) 후보가 없을 때 그냥 원래대로 추출하는 메서드
    def _fallback_extraction(self, text, top_n):
        keywords = self.kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 1), top_n=top_n)
        return [kw[0] for kw in keywords]