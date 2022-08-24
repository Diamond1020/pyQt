import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ui_main import Ui_Dialog
import numpy as np
from nltk.corpus import stopwords
import pandas as pd 
from datetime import datetime
from matplotlib import pyplot as plt
import collections
import re
from wordcloud import WordCloud
import ntpath

import en_core_web_sm
import gensim
import gensim.corpora as corpora

import pyLDAvis 
import pyLDAvis.gensim_models

class MyDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle("CONVERSATION ANALYZER")

        self.setFixedSize(610, 270)

        self.lbl_progress.setText("Please open chart")

        self.btn_openChat.clicked.connect(self.slot_openChat)
        self.btn_openMultiple.clicked.connect(self.slot_openMultiple)
        self.btn_createReport.clicked.connect(self.slot_createReport)

        self.checboxLists = []
        self.checboxLists.append(self.chb_proNames)
        self.checboxLists.append(self.chb_timeframe)
        self.checboxLists.append(self.chb_timestampGraph)
        self.checboxLists.append(self.chb_top20Words)
        self.checboxLists.append(self.chb_wordMap)
        self.checboxLists.append(self.chb_topicModels)

        self.resultPath = "./Result"
        if not os.path.exists(self.resultPath):
            os.mkdir(self.resultPath)

        self.initial()
        
    def initial(self):
        self.files = []
        self.words = []
        self.words_sentence = []
        self.btn_createReport.setEnabled(False)
        self.btn_createReport.show()
        self.wrapper_profileNames = ''
        self.wrapper_timeframe = ''
        self.wrapper_timestampGraph = ''
        self.wrapper_topicModels = ''
        self.wrapper_wordMap = ''
        self.wrapper_top20Words = ''

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileNames, _ = QFileDialog.getOpenFileName(self,"Open Chart File", "","CSV Files (*.csv)", options=options)
        if fileNames:
            self.files = [fileNames]
    
    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileNames, _ = QFileDialog.getOpenFileNames(self,"Open Chart Files", "","CSV Files (*.csv)", options=options)
        if fileNames:
            self.files = fileNames

    def slot_openChat(self):
        self.openFileNameDialog()
        if len(self.files) == 0:
            return
        self.lbl_progress.setText(str(len(self.files)) + " Chart loaded")
        self.btn_createReport.setEnabled(True)

    def slot_openMultiple(self):
        self.openFileNamesDialog()
        if len(self.files) == 0:
            return
        self.lbl_progress.setText(str(len(self.files)) + " Chart loaded")
        self.btn_createReport.setEnabled(True)

    def slot_createReport(self):
        flag = False
        for iter in self.checboxLists:
            if iter.isChecked() == True:
                flag = True
                break

        if flag == False:
            self.lbl_progress.setText("Please check options")
            return

        self.btn_createReport.hide()
        
        for iter, file in enumerate(self.files):
            self.words = []
            self.words_sentence = []
            self.preProcess(file)
            self.outputPath = self.resultPath + "/" + ntpath.basename(file)[0:-4]
            if not os.path.exists(self.outputPath):
                os.mkdir(self.outputPath)
            if not os.path.exists(self.outputPath + '/img'):
                os.mkdir(self.outputPath + '/img')
            self.pos = 0

            filename = self.outputPath + '/index.html'
            f = open(filename,'w')
            wrapper = """<html>
            <head>
            <title>Chart Log Analysis</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
            </head>
            <body>
            <div>%s</div>
            <div>%s</div>
            <div>%s</div>
            <div>%s</div>
            <div>%s</div>
            <div>%s</div>
            </body>
            </html>"""

            if self.chb_topicModels.isChecked() == True:
                self.slot_topicModels()

            whole = wrapper % (self.wrapper_profileNames, self.wrapper_timeframe, self.wrapper_timestampGraph, self.wrapper_top20Words, self.wrapper_wordMap, self.wrapper_topicModels)
            f.write(whole)
            f.close()
        self.initial()

    def preProcess(self, file):
        self.data = pd.read_csv(file) 
        self.stop_words = set(stopwords.words("english"))
        for iter in self.data.Content:
            words_in_quote = re.findall(r'\w+', str(iter))
            filtered_list = [word for word in words_in_quote if word.casefold() not in self.stop_words and not word.isdigit()] 
            self.words += filtered_list
            self.words_sentence.append(filtered_list)

    def slot_profileNames(self):
        profileNames = np.unique(self.data.Author.to_numpy())

        self.pos += 1
        self.wrapper_profileNames = f"""
            <h3>{self.pos}) Profile Names in Conversation Data</h3>"""
        for profileName in profileNames:
            self.wrapper_profileNames += f"""
                <p class="pl-5">- {profileName}</p>"""

    def slot_conversationTimeframe(self):
        timeframe = self.data.Date.iloc[0] + " ~ " + self.data.Date.iloc[-1]

        self.pos += 1
        self.wrapper_timeframe = f"""
            <h3>{self.pos}) Conversation Timeframe</h3>
            <p class="pl-5"><b>{timeframe}</p>"""

    def slot_timestampGraph(self):
        fig, ax = plt.subplots(facecolor=(.38, .51, .51))
        plt.locator_params(axis="x", nbins=15)
        timeline = pd.DataFrame(pd.to_datetime(self.data.Date), columns=['Date'])
        timeline['timestamp'] = [datetime.timestamp(x) for x in timeline.Date]
        ax = timeline['timestamp'].plot(kind='kde')
        x_ticks = ax.get_xticks()
        xlabels = [datetime.fromtimestamp(int(x)) for x in x_ticks]
        ax.set_xticklabels(xlabels)
        fig.autofmt_xdate()
        ax.set_facecolor('#eafff5')
        plt.tight_layout(pad=3)
        plt.savefig(self.outputPath + '/img/activityGraph.png')
        
        self.pos += 1
        self.wrapper_timestampGraph = f"""
            <h3>{self.pos}) Activity Graph of Timestamps in Conversation</h3>
            <p class="pl-5"><img src='./img/activityGraph.png'></p>"""
    
    def slot_top20Words(self):
        Counter = collections.Counter(self.words)
        most_occur = Counter.most_common(20)

        self.pos += 1
        self.wrapper_top20Words = f"""
            <h3>{self.pos}) Top 20 Used Words</h3>
            <div class="pl-5 pr-5">
                <table class="table table-success table-hover">
                    <thead>
                    <tr>
                        <th scope="col">Rank</th>
                        <th scope="col">Word</th>
                    </tr>
                    </thead>
                    <tbody>"""
        for i in range(20):
            self.wrapper_top20Words += f"""
                    <tr>
                        <th scope="row">{i + 1}</th>
                        <td>{most_occur[i][0]}</td>
                    </tr>"""
        self.wrapper_top20Words += """
                    </tbody>
                </table>
            </div>"""

    def slot_wordMap(self):
        comment_words = ''
        for i in range(len(self.words)):
            self.words[i] = self.words[i].lower()
        
        comment_words += " ".join(self.words)+" "
        
        wordcloud = WordCloud(width = 800, height = 800,
                        background_color ='black',
                        stopwords = self.stop_words,
                        min_font_size = 10).generate(comment_words)
        
        plt.figure(figsize = (8, 8), facecolor = None)
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.tight_layout(pad = 0)
        plt.savefig(self.outputPath + '/img/wordMap.png')
        
        self.pos += 1
        self.wrapper_wordMap = f"""
            <h3>{self.pos}) WordMap</h3>
            <p class="pl-5"><img src='./img/wordMap.png'></p>"""

    def slot_topicModels(self):
        bigram = gensim.models.Phrases(self.words_sentence, min_count=5, threshold=100)
        bigram_mod = gensim.models.phrases.Phraser(bigram)
        
        data_words_bigrams = [bigram_mod[doc] for doc in self.words_sentence]
        nlp = en_core_web_sm.load()
        # nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
        allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']
        data_lemmatized = []
        for sent in data_words_bigrams:
            doc = nlp(" ".join(sent)) 
            data_lemmatized.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
        
        id2word = corpora.Dictionary(data_lemmatized)
        texts = data_lemmatized
        corpus = [id2word.doc2bow(text) for text in texts]

        print(corpus)
        print(id2word)
        
        lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                           id2word=id2word,
                                           num_topics=10, 
                                           random_state=100,
                                           update_every=1,
                                           chunksize=100,
                                           passes=15,
                                           alpha='auto',
                                           per_word_topics=True)
                        
        topic_pairs = lda_model.show_topics(num_topics=10, num_words=3, log=False, formatted=False)
        vis = pyLDAvis.gensim_models.prepare(lda_model, corpus, id2word)
        pyLDAvis.save_html(vis, self.outputPath + '/img/topicModeling.html')
        topics = [ [y[0] for y in x[1]] for x in topic_pairs]
        str_topics = [", ".join(x) for x in topics]
        contents =''
        with open(self.outputPath + '/img/topicModeling.html') as f:
            contents = f.read()

        self.pos += 1
        self.wrapper_topicModels = f"""
            <h2>{self.pos}) Identified Topic Models and Themes</h2>
            <div class="pl-5 pr-5">
                <h3>Keyword in the 10 topics</h3>
                <table class="table table-hover table-striped table-sm">
                    <thead class="thead-dark">
                    <tr>
                        <th scope="col">No</th>
                        <th scope="col">Topic Words</th>
                    </tr>
                    </thead>
                    <tbody>"""
        for i in range(10):
            self.wrapper_topicModels += f"""
                    <tr>
                        <th scope="row">{i + 1}</th>
                        <td>{str_topics[i]}</td>
                    </tr>"""
        self.wrapper_topicModels += """
                    </tbody>
                </table>
                <br>
                <h3>Visualize the topics</h3>"""
        self.wrapper_topicModels += contents
        self.wrapper_topicModels += """
            </div>"""
            
    # @pyqtSlot(str)
    # def setProgress(self, value):
    #     self.lbl_progress.setText(value)

    # @pyqtSlot()
    # def threadDeleteLater(self):
    #     self.lbl_progress.setText("Completed!")
    #     self.workerThread.deleteLater()
    #     

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyDialog()
    window.show()
    sys.exit(app.exec_())