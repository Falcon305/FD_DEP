from django.shortcuts import render, redirect
from sklearn.preprocessing import LabelEncoder
from django.contrib import messages, auth
import numpy as np
from .models import Project
from .forms import DocumentForm
import pandas as pd
import io
import os
from django.contrib.auth.decorators import login_required
from sklearn.base import TransformerMixin
import matplotlib.pyplot as plt
from .Algos import *

# Create your views here.
class DataFrameImputer(TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        self.fill = pd.Series([X[c].value_counts().index[0]
            if X[c].dtype == np.dtype('O') else X[c].mean() for c in X],
            index=X.columns)
        return self

    def transform(self, X, y=None):
        return X.fillna(self.fill)


@login_required
def create_project(request):
        form = DocumentForm()
        return render(request, 'processing/create.html', {'form': form})

@login_required
def load_dataset(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                title = request.POST['title']
                if Project.objects.filter(title=title, user=request.user).exists():
                    messages.error(request, 'That title is taken')
                    return redirect('create_project')
                description = request.POST['description']
                newdoc = Project(dataset=request.FILES['dataset'], user=request.user, title=title, description=description)
                newdoc.save()
                file_name = request.FILES['dataset'].name
                df = pd.read_csv("media/user_{0}/raw_csv/{1}".format(request.user, file_name))
                df.columns = df.columns.str.replace(' ', '_')
                buf = io.StringIO()
                df.info(buf=buf)
                s = buf.getvalue()
                lines = s.strip().split('\n')
                entries = lines[1].strip().split()[1]
                size = (' '.join(lines[-1].strip().split()[2:]))
                data_html = df.to_html()
                columns = []
                for col in df.columns:
                    columns.append(col)
                return render(request, 'processing/dataset.html', {'entries': entries,
                                                            'size': size,
                                                            'title': title,
                                                            'loaded_data': data_html,
                                                            'columns': columns,
                                                            'filename':file_name})
            except Exception as e:
                return render(request, 'processing/dataset.html', {"Error": e})
        else:
            return redirect('create_project')
    else:
        return redirect("index")

@login_required
def view_data(request):
    if request.method == 'POST':
        loaded_data = request.POST['loaded_data']
        return render(request, 'processing/view_data.html', {
                                                            'loaded_data': loaded_data,
                                                            })
    else:
        return redirect("index")

@login_required
def preprocessing(request):
    if request.method == 'POST':
        try:
            filename = request.POST['filename']
            date = request.POST['date']
            label = request.POST['label']
            entries = request.POST['entries']
            my_file = "media/user_{0}/raw_csv/{1}".format(request.user, filename)
            df = pd.read_csv(my_file, parse_dates=[date])
            df.columns = df.columns.str.replace(' ', '_')
            df.sort_values(by=[date], inplace=True, ascending=True)
            
            buf = io.StringIO()
            df.info(buf=buf)
            s = buf.getvalue()
            lines = s.strip().split('\n')
            columns = []
            for i in lines[3:-2]:
                i = i.strip().split()
                columns.append(i)
            df = df.replace(0, np.NaN)

            dfi = DataFrameImputer()
            df = dfi.fit_transform(df)

            le = LabelEncoder()
            x_label = df[label]
            df.drop(label, axis=1, inplace=True)
            for i in columns:
                if i[3] == 'object':
                    if i[0] != label:
                        df = pd.concat([df, pd.get_dummies(df[i[0]], prefix=i[0], drop_first=True)], axis=1)
                        df.drop([i[0]], axis=1, inplace=True)
                    else:
                        x_label = le.fit_transform(x_label)
            df = df.assign(label= x_label)
            df = df.rename({'label': label}, axis=1)
            # This will turn all of the string values into category values
            for lb, content in df.items():
                if pd.api.types.is_string_dtype(content):
                    df[lb] = content.astype("category").cat.as_ordered()
            # Fill numeric rows with the median
            for lb, content in df.items():
                if pd.api.types.is_numeric_dtype(content):
                    if pd.isnull(content).sum():
                        # Add a binary column which tells if the data was missing our not
                        df[lb+"_is_missing"] = pd.isnull(content)
                        # Fill missing numeric values with median since it's more robust than the mean
                        df[lb] = content.fillna(content.median())
            if not os.path.exists("media/user_{}/processed_csv".format(request.user)):
                os.makedirs("media/user_{}/processed_csv".format(request.user))
            df.to_csv('media/user_{}/processed_csv/{}'.format(request.user, filename), index=False)
            columns = []
            for col in df.columns:
                columns.append(col)
            '''fig, ax = plt.subplots()
            g = ax.scatter(df[date][:1000], df[label][:1000])'''
            return render(request, 'processing/feature_selection.html', {
                                                                  'columns': columns,
                                                                  'entries' : entries,
                                                                  'label': label,
                                                                  'date': date,
                                                                  'filename':filename
                                                                  })
        except Exception as e:
            return render(request, 'processing/dataset.html', {"Error": e})
    else:
        return redirect("index")

@login_required
def model_selection(request):
    if request.method == 'POST':
        try:
            features = request.POST.getlist('features')
            label = request.POST['label']
            date = request.POST['date']
            filename = request.POST['filename']
            my_file = "media/user_{0}/processed_csv/{1}".format(request.user, filename)
            df = pd.read_csv(my_file, parse_dates=[date])
            buf = io.StringIO()
            df.info(buf=buf)
            s = buf.getvalue()
            lines = s.strip().split('\n')
            entries = lines[1].strip().split()[1]
            ratio = request.POST['ratio']
            return render(request, 'processing/models.html', {
                                                                  'features': features,
                                                                  'ratio' : ratio,
                                                                  'label': label,
                                                                  'date': date,
                                                                  'entries' : entries,
                                                                  'filename':filename
                                                                  })
        except Exception as e:
            return render(request, 'processing/dataset.html', {"Error": e})
    else:
        return redirect("index")

@login_required
def model_exec(request):
    if request.method == 'POST':
        try:
            features = request.POST.getlist('features')
            file_name = request.POST['filename']
            features_list = []
            for feature in features:
                feature = feature[1:-1]
                feature = feature.strip().split(", ")
                for i in feature:
                    features_list.append(i[1:-1])
            label = request.POST['label']
            model = request.POST['model']
            date = request.POST['date']
            ratio = request.POST['ratio']
            return render(request, 'models/' + model + '.html', {"features": features_list,
                                                              "label": label,
                                                              "model": model,
                                                              'date': date,
                                                              'ratio' : ratio,
                                                              "filename": file_name})
        except Exception as e:
            return render(request, 'processing/models.html', {"Error": e})
    else:
        return redirect("index")


