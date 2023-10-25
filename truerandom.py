import os
import openai
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from statsmodels.sandbox.stats.runs import runstest_1samp
import threading
import sys

openai.api_key = os.environ['OPENAI_API_KEY']
byte_length = int(os.environ['BYTE_LENGTH'])
n_index = int(os.environ['N_INDEX'])

print("--- ZERO-SHOT STOCHASTIC BYTE GENERATOR ---\n")


class TimeoutExecutor:
    def __init__(self, timeout, n_index):
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(max_workers=30)
        self.lock = threading.Lock()
        self.results = []
        self.done = False
        self.n_index = n_index
        self.completion_count = -1

    def run(self, func, n):
        start_time = time.time()
        futures = [self.executor.submit(func) for _ in range(n)]
        time_left = self.timeout - (time.time() - start_time)

        for future in as_completed(futures, timeout=time_left):
            try:
                while not future.done():  # while future is not ready
                    time_left = self.timeout - \
                        (time.time() - start_time)  # calculate time left
                    if time_left <= 0:
                        raise TimeoutError()
                    # sleep for a small amount of time to avoid a busy-waiting loop
                    time.sleep(0.01)

                with self.lock:
                    if not self.done:
                        self.results.append(future.result())
                        self.completion_count += 1
                        if self.completion_count % (self.n_index // 10) == 0:
                            print(
                                f'Generating (n={self.n_index}): {int(100 * self.completion_count / self.n_index)}%', end='\r', flush=True)

            except TimeoutError:
                break

        with self.lock:
            self.done = True
        return self.results


stop_array = ['e', 'a', 'r', 'I']


class BitGenerator:
    def __init__(self):
        self.lock = threading.Lock()
        self.failed_requests = 0
        self.int_seq = []
        self.attempt = 1

    def gen_byte(self):
        while self.attempt < 3:  # Max 3 attempts for exponential backoff
            try:
                result = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system",
                               "content": "Choose either 0 or 1. Your answer must only contain the output."}],
                    temperature=1.16,
                    n=byte_length,  # added n parameter to reduce number of requests
                    max_tokens=19,
                    stop=stop_array)
                self.attempt = 1
                # print(result)
                return result

            except openai.OpenAIError as oERR:
                print(f"\n{oERR}\n")
                time.sleep(2 ** self.attempt)  # Exponential backoff
                self.attempt += 1
            except Exception as e:
                print(f'\nUNKNOWN EXCEPTION IN BIT GENERATION: {e}\n')
                time.sleep(2 ** self.attempt)  # Exponential backoff
                self.attempt += 1

    def handle_byte(self):
        n = []
        while len(n) < 8:
            output = self.gen_byte()
            if output is None:  # failure case
                self.failed_requests += 1
                break
            for bit in output['choices']:
                if bit['message']['content'] not in ['0', '1']:
                    continue
                n.append(bit['message']['content'])

        if not n:
            return None

        number = int(''.join(n), 2)
        self.lock.acquire()
        self.int_seq.append(number)
        self.lock.release()


bit_generator = BitGenerator()
completion_count = -1
executor = TimeoutExecutor(timeout=20, n_index=n_index)

print("Initializing...", end='\r', flush=True)

try:
    futures = executor.run(bit_generator.handle_byte, n_index)
except TimeoutError:
    print("Timeout reached, stopping the execution.", end='\r', flush=True)


print(f"\n\nSequence: {bit_generator.int_seq}")
print(f"\nFailed Requests: {bit_generator.failed_requests}")

Z, pval = runstest_1samp(bit_generator.int_seq, correction=False)
print(f"\nRuns Test for Randomness: statistic = {Z}, p-value = {pval}")

print(f"At 5% Significance: {'Little or no evidence against randomness' if (abs(Z)<1.96) else 'There is evidence that the sequence is not random'}")


# TODOs: Measure 0/1 weighting for model, implement additional models.

sys.exit()  # Force exit for hanging requests
