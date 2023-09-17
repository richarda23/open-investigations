
## Intro to prompt engineering.

From LLM bootcamp: https://fullstackdeeplearning.com/llm-bootcamp/spring-2023/

https://fullstackdeeplearning.com/llm-bootcamp/spring-2023/prompt-engineering/


Coverered several tips for prompt engineering

1) Few-shot learning (putting in examples) does not work all that well - the models have been trained. Better to give a really clear prompt. Instead of giving examples of English->French translation, give a prompt (' you are  a masterful translator who will flawlessly translate...'

2) Chain of thought (Cot) examples can help break down complex tasks. By generating reasoning steps it can help provide more context to solve the problem. E.g. showing working for math puzzles

3) ask yourself if subquestions can help break down the task. E.g. 'who lived longer, X or Y?' ask how long did X live? How long did Y live?

4) Provide template structure. E.g. a few lines of import statements, method declarations to help it generate more code

There is no 'theory of prompt engineering', more a 'bag of tricks'

## LLM Ops

https://fullstackdeeplearning.com/llm-bootcamp/spring-2023/llmops/
https://youtu.be/Fquj2u7ay40?list=PL1T8fO7ArWleyIqOy37OVXsP4hFXymdOZ

How to test, evaluate, prepare for production

### What model to use

- GPT-4 best (as of May 2023). Use this unless you have:
- cost, speed or privacy requirements. GPT-3.5 or Claude (Anthropic) are cheaper/faster.
- OSS models will catch up but few are as capable or have open licenses.


### Testing

- how to evaluate your prompts?
- build a dataset of inputs that are difficult or interesting, so you can see how they change over time.
- can this be automated?
  Training metrics (overfitting vs drift vs domain shift - at 22.46 in video)

#### Evaluation methods

* actual accuracy (if question has a single correct answer)
* semantic similarity to a reference answer.
* semantic similarity to a previous answer.
* human evaluation
* ask another LLM if this is a good answer or not.
* if none of the above - static analysis (e.g. is it formatted correctly)

### Deployment

* get as much user feedback as possible. Thump up /down. Add 'bad' answers to your test set


## Language UIs (LUIs)

https://fullstackdeeplearning.com/llm-bootcamp/spring-2023/ux-for-luis/

- regular design principles are still relevant
- Different types: chat-to-chat (ChatGPT), in-place prompts (CoPilot), popups (replit)
- What are consequences of wrong answer and how capabable is your service (subhuman, human or superhuman) (matrix)
- How important is accuracy ? (Importance proportional to effort needed - Copilot is static autocomplete so has low threshold, for ChatGPT we are asking for replies so expect nore accuracy
- how important is latency( for copilot ,needs to be fast; for ChatGPT it needs to be as fast as your reading speed)
- how can you get feedback? acceptance of a suggestion is clear 'thumbs up' signal for Copilot, harder to get for ChatGPT. Midjourney forces user to choose between 4 images before being able to save.

Compares Bing (rushed, got bad feedback loops as it read current internet about itself); vs Coplilot (Well researched and thought-out)






