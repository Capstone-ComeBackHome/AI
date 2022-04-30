import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import torch
from torch import nn
from torch.utils.data import DataLoader

from kobert import get_pytorch_kobert_model
from kobert import get_tokenizer
import gluonnlp as nlp


le = LabelEncoder()
le.classes_ = np.load('classes.npy', allow_pickle = True)

class BERTClassifier(nn.Module):
    def __init__(self,
                 bert,
                 hidden_size = 768,
                 num_classes=len(le.classes_),
                 dr_rate=None,
                 params=None):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.dr_rate = dr_rate

        self.classifier = nn.Linear(hidden_size , num_classes)
        if dr_rate:
            self.dropout = nn.Dropout(p=dr_rate)

    def gen_attention_mask(self, token_ids, valid_length):
        attention_mask = torch.zeros_like(token_ids)
        for i, v in enumerate(valid_length):
            attention_mask[i][:v] = 1
        return attention_mask.float()

    def forward(self, token_ids, valid_length, segment_ids):
        attention_mask = self.gen_attention_mask(token_ids, valid_length)

        _, pooler = self.bert(input_ids = token_ids, token_type_ids = segment_ids.long(), attention_mask = attention_mask.float().to(token_ids.device))
        if self.dr_rate:
            out = self.dropout(pooler)
        else:
            out = pooler
        return self.classifier(out)


def load_diag_model():
    kobert_model, vocab = get_pytorch_kobert_model()
    model = BERTClassifier(kobert_model)
    model.load_state_dict(torch.load('../saved_model/kobert1_state_dict.pth',  map_location=torch.device('cpu')))
    model.eval()

    tokenizer = get_tokenizer()
    tok = nlp.data.BERTSPTokenizer(tokenizer, vocab, lower=False)
    transform = nlp.data.BERTSentenceTransform(tok, max_seq_length=128, pad=True, pair=False)
    return model, transform

model, transform = load_diag_model()

def predict(sentence):
    with torch.no_grad():
        input = transform([sentence])
        dataloader = torch.utils.data.DataLoader(input, batch_size=1)
        token_ids, valid_length, segment_ids = dataloader
        token_ids = token_ids.long()
        valid_length = valid_length
        segment_ids = segment_ids.long()
        out = model(token_ids, valid_length, segment_ids)

    top3 = torch.topk(out, k = 3, dim = 1, sorted = True).indices[0].numpy()
    diseaseList = le.inverse_transform(top3)
    return diseaseList
