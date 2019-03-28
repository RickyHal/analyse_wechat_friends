#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import itchat
import jieba
import math
from pyecharts import Pie, Geo, WordCloud
import PIL.Image as Image


class Analyse(object):

    def __init__(self, friends, uuid):
        super(Analyse, self).__init__()
        self.friends = friends
        # 停用词文件
        self.break_words_file = '哈工大停用词.txt'
        # 停用词
        self.break_words = []
        self.uuid = uuid

    # 生成男女性别比例图
    def friends_sex_ratio(self):
        sex = ['未知', '男', '女']
        ratio = [0, 0, 0]
        for item in self.friends:
            ratio[item['Sex']] += 1
        pie = Pie(self.friends[0]['NickName'] +
                  "的微信好友性别比例", title_pos='center')
        pie.add(
            "",
            sex,
            ratio,
            radius=[40, 75],
            label_text_color=None,
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
            background_color='#FFF'
        )
        pie.render('./html/%s_sex_ratio.html' % self.uuid)
        pie.render(path='./img/%s_sex_ratio.png' % self.uuid)
        # 通过文件传输助手发送到自己微信中
        itchat.send_image('./img/%s_sex_ratio.png' %
                          self.uuid, 'filehelper')

    # 生成好友地图分布图和热力图
    def friends_map(self):
        citys = []
        values = []
        geo = Geo(
            self.friends[0]['NickName'] + "的微信好友分布图",
            title_color="#fff",
            title_pos="center",
            width='100wh',
            height='100vh',
            background_color="#404a59",
        )
        for item in self.friends:
            if item['City'] not in citys and item['City'] and self.is_chinese(item['City']):
                citys.append(item['City'])
                values.append(1)
            elif item['City'] and self.is_chinese(item['City']):
                values[citys.index(item['City'])] += 1
        types = ['heatmap', 'scatter']
        for item in types:
            geo.add(
                "",
                citys,
                values,
                visual_range=[0, max(values)],
                visual_text_color="#fff",
                symbol_size=15,
                # type为地图样式，scatter为地图，heatmap为热力图
                type=item,
                tooltip_formatter="{b}：{c}",
                is_visualmap=True,
                background_color='#FFF'
            )
            geo.render('./html/%s_frends_city_%s.html' %
                       (self.uuid, item))
            geo.render(path='./img/%s_frends_city_%s.png' %
                       (self.uuid, item))
            itchat.send_image('./img/%s_frends_city_%s.png' %
                              (self.uuid, item), 'filehelper')

    # 判断是否是中文
    def is_chinese(self, words):
        for word in words:
            if not(u'\u4e00' <= word <= u'\u9fa5'):
                return False
        return True

    # 获取停用词
    def get_break_stopWords(self):
        with open(self.break_words_file, 'r', encoding='UTF-8-sig') as f:
            for line in f:
                self.break_words.append(line.replace('\n', ''))
        f.close()

    # 删除停用词以及非中文
    def delete_break_words(self, word):
        if word not in self.break_words:
            if self.is_chinese(word):
                return word

    # 生成好友签名词云
    def signature_cloud(self):
        words = []
        count = []
        # 获取停用词
        self.get_break_stopWords()
        # 清洗、统计数据
        for item in self.friends:
            for word in jieba.lcut(item['Signature']):
                if word not in words and self.is_chinese(word):
                    words.append(self.delete_break_words(word))
                    count.append(1)
                elif self.is_chinese(word):
                    count[words.index(self.delete_break_words(word))] += 1
        wordcloud = WordCloud('%s的微信好友签名词云' % self.friends[0]['NickName'], width=1300,
                              height=620, background_color='#FFF', title_pos='center')
        wordcloud.add("", words, count, shape='circle')
        wordcloud.render('./html/%s_signature_word_cloud.html' % self.uuid)
        wordcloud.render(
            path='./img/%s_signature_word_cloud.png' % self.uuid)
        itchat.send_image('./img/%s_signature_word_cloud.png' %
                          self.uuid, 'filehelper')

    # 将所有好友的头像拼成一张图
    def head_img_cloud(self):
        num = 1
        for item in self.friends:
            print('当前下载：第%d个好友的头像，昵称：%s' % (num, item['NickName']))
            img = itchat.get_head_img(userName=item["UserName"])
            with open('./head_img/%s_head_img-%d.jpg' % (self.uuid, num), 'wb') as f:
                f.write(img)
            f.close()
            num += 1
        print('开始生成图云...')
        each_size = int(math.sqrt(float(640 * 640) / len(self.friends)))
        lines = int(640 / each_size)
        # 生成白色背景新图片
        image = Image.new('RGBA', (640, 640), 'white')
        # 拼接好友头像
        x = 0
        y = 0
        for i in range(1, len(self.friends)):
            try:
                # 读取头像文件
                img = Image.open('./head_img/%s_head_img-%d.jpg' %
                                 (self.uuid, i))
            except Exception as e:
                print(e)
            else:
                # 设置头像图片尺寸
                img = img.resize((each_size, each_size), Image.ANTIALIAS)
                # 粘贴好友头像到指定的位置
                image.paste(img, (x * each_size, y * each_size))
                x += 1
                if x == lines:
                    x = 0
                    y += 1
        image.save("./img/%s_all_head_img.png" % self.uuid)
        print('生成完成')
        itchat.send_image("./img/%s_all_head_img.png" %
                          self.uuid, 'filehelper')

if __name__ == "__main__":
    # 登录微信
    itchat.auto_login(hotReload=True)
    friends = itchat.get_friends(update=True)
    analyse = Analyse(friends, itchat.get_QRuuid())
    # analyse.friends_sex_ratio()
    # analyse.friends_map()
    analyse.signature_cloud()
    # analyse.head_img_cloud()
