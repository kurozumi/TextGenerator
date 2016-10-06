# -*- coding: utf-8 -*-

import re
import MeCab
import sqlite3

from collections import defaultdict

BEGIN = "__BIGIN__"
END = "__END__"


class Chain(object):

    def __init__(self):
        # 形態素解析用タガー
        self.tagger = MeCab.Tagger('-Ochasen')

    def parse(self, sentence):
        words = [BEGIN]

        self.tagger.parse("")
        node = self.tagger.parseToNode(sentence)

        while node:
            if node.posid != 0:
                words.append(node.surface)
            node = node.next
        words.append(END)
        
        return words

    def ngram(self, words, N=3):

        model = defaultdict(int)

        if len(words) < N:
            return {}

        # 繰り返し
        for i in range(len(words)-N+1):
            model[tuple(words[i:i+N])] += 1

        return model 

    def splitlines(self, sentence):
        # 改行文字以外の分割文字（正規表現表記）
        delimiter = "。|．|\."

        # 全ての分割文字を改行文字に置換（splitしたときに「。」などの情報を無くさないため）
        sentence = re.sub(r"({0})".format(delimiter), r"\1\n", sentence)

        # 改行文字で分割
        for sentence in sentence.splitlines():
            yield sentence

    def fit(self,sentence, N=3):

        model = defaultdict(int)
        
        for sentence in self.splitlines(sentence):
            # 文章を単語に分ける
            words = self.parse(sentence)
            # N-Gramモデルを作り出現頻度をカウントする 
            words = self.ngram(words, N=N)

            for (word,n) in words.items():
                model[word] += n

        return model
 
    DB_PATH = "chain.db"
    DB_SCHEMA_PATH = "schema.sql"
    
    def save(self, triplet_freqs, init=False):
        u"""
        3つ組毎に出現回数をDBに保存
        @param triplet_freqs 3つ組とその出現回数の辞書 key: 3つ組（タプル） val: 出現回数
        """
        
        # DBオープン
        con = sqlite3.connect(self.DB_PATH)

        # 初期化から始める場合
        if init:
            # DBの初期化
            with open(self.DB_SCHEMA_PATH, "r") as f:
                schema = f.read()
                con.executescript(schema)

            # データ整形
            datas = [(triplet[0], triplet[1], triplet[2], freq) for (triplet, freq) in triplet_freqs.items()]

            # データ挿入
            p_statement = u"insert into chain_freqs (prefix1, prefix2, suffix, freq) values (?, ?, ?, ?)"
            con.executemany(p_statement, datas)

        # コミットしてクローズ
        con.commit()
        con.close()

    def show(self, words):
        for word in words:
            print("|".join(word), "\t", words[word])
            print("=====")


if __name__ == '__main__':

    # 『檸檬』梶井基次郎
    sentence = """仲間達よ立ち上がれ

今日の勝利つかもうぜ

共に戦おう

拳を突き上げろ

今だ本物の英雄になりに行こう

夢が叶うまで全力で走り抜け


オーオーオー、我等は生きる

オーオーオー、オー！ファジの為

オー！ファジの為

オー！ファジの為

オー！ファジの為


全てはファジの為

全てはファジの為

全てはファジの為

全てはファジの為


シャララーラ

シャララーラ

シャララーラ

シャララーラ

シャララーラ

シャララーラ

シャララーラ

シャララーラ"""

    # chain = Chain(sentence)
    # freqs = chain.fit()
    # chain.show(freqs)
    # chain.save(freqs, True)

    chain = Chain()
    result = chain.fit(sentence)
    chain.show(result)
    # chain.save(result, True)
