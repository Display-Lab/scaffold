import warnings
import time
import logging
import random
import io
#from asyncore import read
from io import StringIO
from rdflib import Literal, URIRef, BNode
from rdflib.namespace import RDF
from decimal import *



# from .load_for_real import load
# from load import read, transform,read_contenders,read_measures,read_comparators
# from score import score, select,apply_indv_preferences,apply_history_message

# load()

warnings.filterwarnings("ignore")
# TODO: process command line args if using graph_from_file()
# Read graph and convert to dataframe
start_time = time.time()
class Esteemer():
    def __init__(self, spek_tp,measure_list, preferences , history,mpm_df):
        self.y=[]
        self.spek_tp=spek_tp
        self.preferences=preferences
        self.history=history
        self.mpm_df=mpm_df
        self.s=URIRef("http://example.com/app#display-lab")
        self.p=URIRef("http://example.com/slowmo#HasCandidate")
        self.p1=URIRef("slowmo:acceptable_by")
        self.p2=URIRef('http://example.com/slowmo#Score')
        self.o2=Literal(1)
        self.gap_dicts={}
        self.trend_slopes={}
        self.losses={}
        self.acheivements={}
        self.measure_list=measure_list
        self.measure_gap_list=[]
        self.measure_gap_list_new=[]
        # self.measure_gap_list.append("gaps")
        self.measure_trend_list=[]
        self.measure_trend_list_new=[]
        # self.measure_trend_list.append("slopes")
        self.measure_acheivement_list=[]
        self.measure_acheivement_list_new=[]
        # self.measure_acheivement_list.append("acheivement")
        self.measure_loss_list=[]
        self.measure_loss_list_new=[]
        # self.measure_loss_list.append("loss")
        self.gap_dict={}
        self.trend_dict={}
        self.acheivement_dict={}
        self.loss_dict={}
        self.message_recency={}
        self.message_received_count={}
        self.measure_recency={}
        self.preferences={}
        for s,p,o in self.spek_tp.triples( (self.s, self.p, None) ):
            s1= o
            for s,p,o in self.spek_tp.triples((s1,self.p1,None)):
                self.spek_tp.add((s,self.p2,self.o2))
                self.y.append(s)
                # print(s)
    def process_spek(self):
        # print(*self.y)
        sh=BNode("p1")
        ph=URIRef("http://purl.obolibrary.org/obo/RO_0000091")
        p4=URIRef("http://example.com/slowmo#RegardingMeasure")
        p5=URIRef("http://example.com/slowmo#RegardingComparator")
        ph33=URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        ph3=URIRef("http://purl.obolibrary.org/obo/PSDO_0000099")
        ph4=URIRef("http://purl.obolibrary.org/obo/PSDO_0000100")
        ph5=URIRef("http://purl.obolibrary.org/obo/PSDO_0000105")
        ph6=URIRef("http://purl.obolibrary.org/obo/PSDO_0000104")
        ph7=URIRef("http://purl.obolibrary.org/obo/PSDO_0000113")
        ph8=URIRef("http://purl.obolibrary.org/obo/PSDO_0000112")
        ph9=URIRef("http://example.com/slowmo#PerformanceGapSize")
        ph10=URIRef("http://example.com/slowmo#PerformanceTrendSlope")
        ph11=URIRef("http://example.com/slowmo#TimeSinceLastLoss")
        ph12=URIRef("http://example.com/slowmo#TimeSinceLastAcheivement")
        loss=[]
        # loss.append("loss")
        acheivement=[]
        # acheivement.append("acheivement")
        gaps=[]
        
        trend_slope=[]
        self.measure_gap_list=[]
        # self.measure_gap_list.append("gaps")
        self.measure_trend_list=[]
        # self.measure_trend_list.append("slopes")
        self.measure_acheivement_list=[]
        # self.measure_acheivement_list.append("acheivement")
        self.measure_loss_list=[]
        # self.measure_loss_list.append("loss")
        
        Measure4=None
        Measure =None
        Measure1=None
        Measure2=None
        Measure3=None
        for x in self.measure_list:
            Measure =x
            for ss,ps,os in self.spek_tp.triples((sh,ph,None)):
                s6=os
                for s123,p123,o123 in self.spek_tp.triples((s6,ph33,None)):
                    if o123 == ph5 or o123 == ph6:
                        for s124,p124,o124 in self.spek_tp.triples((s6,p4,None)):
                            o124=str(o124)
                            if o124 ==Measure:
                                # print(Measure)
                                gaps.clear()
                                for s1234,p1234,o1234 in self.spek_tp.triples((s6,p5,None)):
                                    # print(o1234)
                                    for s125,p125,o125 in self.spek_tp.triples((s6,ph9,None)):
                                        # print(str(o125))
                                        gaps.append(str(o1234))
                                        gaps.append(Measure)
                                        gaps.append(float(o125))
                                        gaps_tuples=tuple(gaps)
                                        self.measure_gap_list.append(gaps_tuples)
                    if o123 == ph3 or o123 ==ph4:
                        for s124,p124,o124 in self.spek_tp.triples((s6,p4,None)):
                            o124=str(o124)
                            if o124 ==Measure:
                                trend_slope.clear() 
                                for s1234,p1234,o1234 in self.spek_tp.triples((s6,p5,None)):
                                    for s125,p125,o125 in self.spek_tp.triples((s6,ph10,None)):
                                        # print(str(o125))
                                        trend_slope.append(str(o1234))
                                        trend_slope.append(Measure)
                                        trend_slope.append(float(o125))
                                        trend_tuples=tuple(trend_slope)
                                        self.measure_trend_list.append(trend_tuples)
                    if o123 == ph7 :
                        for s124,p124,o124 in self.spek_tp.triples((s6,p4,None)):
                            o124=str(o124)
                            if o124 ==Measure:
                                acheivement.clear() 
                                for s1234,p1234,o1234 in self.spek_tp.triples((s6,p5,None)):
                                    for s125,p125,o125 in self.spek_tp.triples((s6,ph12,None)):
                                        # print(str(o125))
                                        acheivement.append(str(o1234))
                                        acheivement.append(Measure)
                                        acheivement.append(float(o125))
                                        acheivement_tuples=tuple(acheivement)
                                        self.measure_acheivement_list.append(acheivement_tuples)
                    
                    if o123 == ph8 :
                        for s124,p124,o124 in self.spek_tp.triples((s6,p4,None)):
                            o124=str(o124)
                            if o124 ==Measure:
                                loss.clear() 
                                for s1234,p1234,o1234 in self.spek_tp.triples((s6,p5,None)):
                                    for s125,p125,o125 in self.spek_tp.triples((s6,ph11,None)):
                                        # print(str(o125))
                                        loss.append(str(o1234))
                                        loss.append(Measure)
                                        loss.append(float(o125))
                                        loss_tuples=tuple(loss)
                                        self.measure_loss_list.append(loss_tuples)
        self.measure_loss_list = list(set(self.measure_loss_list))
        for x in self.measure_loss_list:
            x=list(x)
            self.measure_loss_list_new.append(x)
        # print(*self.measure_loss_list_new)
        # print(*self.measure_loss_list)
        self.measure_acheivement_list = list(set(self.measure_acheivement_list))
        for x in self.measure_acheivement_list:
            x=list(x)
            self.measure_acheivement_list_new.append(x)
        # print(*self.measure_acheivement_list_new)
        # print(*self.measure_acheivement_list) 
        self.measure_trend_list = list(set(self.measure_trend_list))
        for x in self.measure_trend_list:
            x=list(x)
            self.measure_trend_list_new.append(x)
        # print(*self.measure_trend_list_new)                 
        self.measure_gap_list = list(set(self.measure_gap_list))
        for x in self.measure_gap_list:
            x=list(x)
            self.measure_gap_list_new.append(x)
        # print(*self.measure_gap_list_new)                        
                           
    def process_history(self):
        def extract(a):
    #recursive algorithm for extracting items from a list of lists and items
            if type(a) is list:
                l = []
                for item in a:
                    l+=extract(item)
                return l
            else:
                return [a]
        
        Message_received_count=[]
        causal_pathways=[]
        causal_pathways1=[]
        message_recency={}
        a=[]
        i=0
        for k,v in self.history.items():
            
            i=i+1
            for k1,v1 in v.items():
                # print(k)
                # print(k1)
                if k1 == "Text":
                    Message_received_count.append(v1)
                if k1=="Causal_pathways":
                    causal_pathways.append(v1)
                    # i=i+1
                    message_recency[i]=v1
                 
        causal_pathways=extract(causal_pathways)
        # print(*causal_pathways)
        for x in causal_pathways:
            x=x.replace("social ","")
            x=x.replace("goal ","")
            causal_pathways1.append(x)

            # print(x)
            # print("\n")
        # print(*causal_pathways1)
        my_dict = {i:causal_pathways1.count(i) for i in causal_pathways1}
        
        
        # for k2,v2 in message_recency.items():
        #     print(k2,v2)


        
        # f.close()
    
    def process_mpm(self):
        # for col in self.mpm_df:
        #     print(col)
        self.gap_dict = dict(zip(self.mpm_df.Causal_pathway, self.mpm_df.Comparison_size))
        # for k,v in self.gap_dict.items():print(k, v)
        self.trend_dict = dict(zip(self.mpm_df.Causal_pathway, self.mpm_df.Trend_slope))
        # for k,v in self.gap_dict.items():print(k, v)
        self.acheivement_dict = dict(zip(self.mpm_df.Causal_pathway, self.mpm_df.Measure_achievement_recency))
        # for k,v in self.acheivement_dict.items():print(k, v)
        self.loss_dict=dict(zip(self.mpm_df.Causal_pathway, self.mpm_df.Loss_recency))
        # for k,v in self.loss_dict.items():print(k, v)
        self.message_recency=dict(zip(self.mpm_df.Causal_pathway, self.mpm_df.Message_recency))
        # for k,v in self.message_recency.items():print(k, v)
        self.measure_recency=dict(zip(self.mpm_df.Causal_pathway, self.mpm_df.Measure_recency))
        # for k,v in self.measure_recency.items():print(k, v)
    
    def score(self):
        # print(*self.measure_gap_list) 
        j_new=()
        a_new=[]
        for i in self.y:
            # print(i)
            s = i
            pwed = URIRef("slowmo:acceptable_by")
            p3=URIRef("http://purl.obolibrary.org/obo/RO_0000091")
            ph33=URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
            ph5=URIRef("http://purl.obolibrary.org/obo/PSDO_0000105")
            ph6=URIRef("http://purl.obolibrary.org/obo/PSDO_0000104")
            ph3=URIRef("http://purl.obolibrary.org/obo/PSDO_0000099")
            ph4=URIRef("http://purl.obolibrary.org/obo/PSDO_0000100")
            p4=URIRef("http://example.com/slowmo#RegardingComparator")
            ph7=URIRef("http://purl.obolibrary.org/obo/PSDO_0000113")
            ph8=URIRef("http://purl.obolibrary.org/obo/PSDO_0000112")

            # for s2we,p2we,o2we in self.spek_tp.triples((s,pwed,None)):
            #     print(o2we)
                # o2wea.append(o2we)
            for s5,p5,o5 in self.spek_tp.triples((s,p3,None)):
                for s2we,p2we,o2we in self.spek_tp.triples((s,pwed,None)):
                    o2we=str(o2we)
                    # print(o2we)
                    if "Gain" in str(o2we):
                        o2we= "Achievement"
                    if "better" in str(o2we):
                        o2we="Better"
                    if "Worse" in str(o2we):
                        o2we="Worse"
                # print(o5)
                    print(o2we)
                    s6=o5
                    # for s8,p8,o8 in self.spek_tp.triples((s6,p5,None)):
                    #             print(s6)
                    for s7,p7,o7 in self.spek_tp.triples((s6,ph33,None)):
                        #gap_multiplication
                        if o7==ph5 or o7==ph6:
                            for s7,p7,o7 in self.spek_tp.triples((s6,p4,None)):
                                a=[item for item in self.measure_gap_list_new if str(o7) in item]
                                for k,v in self.gap_dict.items():
                                    if k == o2we:
                                        for j in a:
                                            if v == "--":
                                                v=0
                                            v= float(v)
                                            j[2]=j[2]*v
                        #trend multiplication
                        if o7==ph3 or o7==ph4:    
                            for s8,p8,o8 in self.spek_tp.triples((s6,p4,None)):
                                b=[item for item in self.measure_trend_list_new if str(o8) in item]
                                # print(*b)
                                # print("before")
                                for k,v in self.trend_dict.items():
                                    if k == o2we:
                                        for j in b:
                                            if v == "--":
                                                v=0
                                            v= float(v)
                                            j[2]=j[2]*v
                                # print(*b)
                        if o7==ph7:
                            # print(o2we)    
                            for s8,p8,o8 in self.spek_tp.triples((s6,p4,None)):
                                c=[item for item in self.measure_acheivement_list_new if str(o8) in item]
                                # print(*c)
                                # print("multiplication")
                                for k,v in self.acheivement_dict.items():
                                    # print(o2we)
                                    if "Achievement" == o2we:
                                        # print(o2we)
                                        for j in c:
                                            # print(*j)
                                            if v == "--":
                                                v=0
                                            v= float(v)
                                            j[2]=Decimal(j[2])*Decimal(v)
                                # print(*c)
                                # print("\n")
                        if o7==ph8:    
                            for s8,p8,o8 in self.spek_tp.triples((s6,p4,None)):
                                d=[item for item in self.measure_gap_list if str(o8) in item]
                                #print(*d)
                # print("\n")

    def select(self):
        self.scores=[]
        nodes=[]
        # print(*self.y)
        if len(self.y)!=0:
            self.node=random.choice(self.y)
        else:
            self.node="No message selected"

        if self.node== "No message selected":
            return self.node,self.spek_tp
        else:
            o2=URIRef("http://example.com/slowmo#selected")
            self.spek_tp.add((self.node,RDF.type,o2))
            return self.node,self.spek_tp

    def get_selected_message(self):
        s_m={}
        if self.node== "No message selected":
            s_m["text"]="No message selected"
            return s_m 
        else:
            s=self.node
            p1=URIRef("psdo:PerformanceSummaryTextualEntity")
            pwed=URIRef("slowmo:acceptable_by")
            p3=URIRef("http://purl.obolibrary.org/obo/RO_0000091")
            p4=URIRef("http://example.com/slowmo#RegardingMeasure")
            p8=URIRef("http://example.com/slowmo#name")
            p10= URIRef("http://purl.org/dc/terms/title")
            p12=URIRef("http://purl.obolibrary.org/obo/IAO_0000573")
            p13=URIRef("http://purl.obolibrary.org/obo/STATO_0000166")
            p20=URIRef("http://example.com/slowmo#AncestorTemplate")
            pqd=URIRef("http://example.com/slowmo#PerformanceGapSize")
            pqw=URIRef("http://example.com/slowmo#PerformanceTrendSlope")
            p232= URIRef("psdo:PerformanceSummaryDisplay")
            Display=["Text-only", "bar chart", "line graph"]
            sw=0
            o2wea=[]
            
            
            for s21,p21,o21 in self.spek_tp.triples((s,p20,None)):
                s_m["Template ID"] = o21
            for s2,p2,o2 in self.spek_tp.triples((s,p1,None)):
                s_m["text"] = o2
            # for s212,p212,o212 in self.spek_tp.triples((s,p232,None)):
               
            s_m["Display"]=random.choice(Display)
            for s9,p9,o9 in self.spek_tp.triples((s,p8,None)):
                s_m["Comparator Type"] = o9
            for s2we,p2we,o2we in self.spek_tp.triples((s,pwed,None)):
                o2wea.append(o2we)
            # print(*o2wea)
            s_m["Acceptable By"] = o2wea

            
            
            

            
                
            

            for s5,p5,o5 in self.spek_tp.triples((s,p3,None)):
                s6=o5
                # print(o5)
                for s7,p7,o7 in self.spek_tp.triples((s6,p4,None)):
                    s_m["Measure Name"]=o7
                    s10= BNode(o7)
                    for s11,p11,o11 in self.spek_tp.triples((s10,p10,None)):
                        s_m["Title"]=o11
                for s14,p14,o14 in self.spek_tp.triples((s6,RDF.type,None)):
                    #print(o14)
                    if o14==p12:
                        s_m["Display"]="line graph"
                        sw=1
                    if o14==p13:
                        s_m["Display"]="bar chart"
                        if sw==1:
                            s_m["Display"]= "line graph,bar chart"
                

            
                  

            
            return s_m
    
# logging.critical("--score and select %s seconds ---" % (time.time() - start_time1))
# print(finalData)

# time_taken = time.time()-start_time
logging.critical("---total esteemer run time according python script %s seconds ---" % (time.time() - start_time))

"""with open('data.json', 'a') as f:
    f.write(finalData + '\n')"""
