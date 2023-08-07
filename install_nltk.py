import nltk

for resource in (
    'tagsets',
    'punkt',
    'averaged_perceptron_tagger'
):
  nltk.download(resource)
