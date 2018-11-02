import os
import random
import jieba
import jieba.analyse


def TextProcessing(words):
    # word_cut = jieba.cut(words, cut_all=False)  # 精简模式，返回一个可迭代的generator
    # word_list = list(word_cut)  # generator转换为list
    # return word_list
    # seg = jieba.cut_for_search(words)  # 搜索引擎模式
    # seg_list = list(seg)
    #
    # print(", ".join(seg_list))
    # return seg_list
    keywords = jieba.analyse.extract_tags(words, topK=20, withWeight=True, allowPOS=('n', 'nr', 'ns', 'nz', 'd', 'nt', 'v', 'vn', 'i'))
    # print(keywords)
    # print(type(keywords))
    # <class 'list'>
    item_list = []
    for item in keywords:
        # print(item)
        # print(item[0], item[1])
        all_item = {}

        all_item['words'] = item[0]
        all_item['weight'] = item[1]
        item_list.append(all_item)

    return item_list


def MakeWordsSet(words_file):
    words_set = set()                                            # 创建set集合
    with open(words_file, 'r', encoding='utf-8') as f:        # 打开文件
        for line in f.readlines():                                # 一行一行读取
            word = line.strip()                                    # 去回车
            if len(word) > 0:                                    # 有文本，则添加到words_set中
                words_set.add(word)
    return words_set                                             # 返回处理结果


def words_dict(all_words_list,deleteN,stopwords_set=set()):
    feature_words = []   # 特征列表
    n = 1
    for t in range(deleteN, len(all_words_list), 1):
        if n > 1000:  # feature_words的维度为1000
            break
        # 如果这个词不是数字，并且不是指定的结束语，并且单词长度大于1小于5，那么这个词就可以作为特征词
        if not all_words_list[t]['words'].isdigit() and all_words_list[t]['words'] not in stopwords_set and 1 < len(all_words_list[t]['words']) < 5:
            feature_words.append(all_words_list[t])
        n += 1
    # print(feature_words)
    return feature_words


if __name__ == '__main__':
    # 文本预处理
    # folder_path = './SogouC/Sample'                #训练集存放地址
    # all_words_list, train_data_list, test_data_list, train_class_list, test_class_list = TextProcessing(folder_path, test_size=0.2)
    all_words_list = TextProcessing('新浪新闻-“断交”民进党真急了 恼羞成怒喊“换不来统一”')

    # 生成stopwords_set
    stopwords_file = './stopwords_cn.txt'
    stopwords_set = MakeWordsSet(stopwords_file)

    feature_words = words_dict(all_words_list, 2, stopwords_set)
    print(feature_words)