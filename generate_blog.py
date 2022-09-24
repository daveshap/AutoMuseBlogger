import re
import os
import openai
import textwrap
from time import time,sleep
from pprint import pprint


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


openai.api_key = open_file('openaiapikey.txt')


def gpt3_completion(prompt, engine='text-davinci-002', temp=0.7, top_p=1.0, tokens=1000, freq_pen=0.0, pres_pen=0.0, stop=['asdfasdf', 'asdasdf']):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()  # force it to fix any unicode errors
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            #text = re.sub('\s+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            save_file('gpt3_logs/%s' % filename, prompt + '\n\n==========\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


def improve_outline(request, outline):
    prompt = open_file('prompt_improve_outline.txt').replace('<<REQUEST>>',request).replace('<<OUTLINE>>', outline)
    outline = '1. ' + gpt3_completion(prompt)
    return outline


def neural_recall(request, section):
    prompt = open_file('prompt_section_research.txt').replace('<<REQUEST>>',request).replace('<<SECTION>>',section)
    notes = gpt3_completion(prompt)
    return notes


def improve_prose(research, prose):
    prompt = open_file('prompt_improve_prose.txt').replace('<<RESEARCH>>',research).replace('<<PROSE>>', prose)
    prose = gpt3_completion(prompt)
    return prose


if __name__ == '__main__':
    request = open_file('request.txt')
    # build the outline
    prompt = open_file('prompt_outline.txt').replace('<<REQUEST>>',request)
    outline = '1. ' + gpt3_completion(prompt)
    print('\n\nOUTLINE:', outline)
    for i in list(range(0,2)):
        outline = improve_outline(request, outline)
        print('\n\nIMPROVED OUTLINE:', outline)
    outline = outline.replace('\n\n', '\n')
    sections = outline.splitlines()
    final_blog = list()
    for section in sections:
        # research
        research = ''
        print('\n\nSECTION:', section)
        for i in list(range(0,2)):
            result = neural_recall(request, section)
            research = research + '\n%s' % result
            print('\n\nRESEARCH:', research)
        research = research.strip()
        # first draft
        prompt = open_file('prompt_section_prose.txt').replace('<<RESEARCH>>', research)
        prose = gpt3_completion(prompt)
        print('\n\nPROSE:', prose)
        for i in list(range(0,2)):
            prose = improve_prose(research, prose)
            print('\n\nPROSE:', prose)
        final_blog.append(prose)
    pprint(final_blog)
    output = '\n\n'.join(final_blog)
    save_file('blog.txt', output)