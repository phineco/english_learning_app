<template>
    <div id="app" class="container">
        <h1>English Read-Aloud Practice</h1>

        <div class="reference-text-container">
            <h2>Reference Text:</h2>
            <p class="reference-text" v-if="displayWords.length">
                <span v-for="(word, index) in displayWords" :key="index" :class="getWordClass(word)">
                    {{ word.text + ' ' }}
                </span>
            </p>
            <p v-else>{{ referenceText }}</p>
            <p>Total words: {{ totalOriginalWords }}</p>
        </div>

        <div class="controls">
            <button @click="startRecognition" :disabled="isRecognizing || !isSpeechRecognitionSupported"
                class="btn btn-primary">
                {{ isRecognizing ? 'Listening...' : 'Start Reading Aloud' }}
            </button>
            <button @click="stopRecognition" :disabled="!isRecognizing" class="btn btn-danger">
                Stop
            </button>
            <p v-if="!isSpeechRecognitionSupported" class="text-danger">
                Speech Recognition API is not supported in your browser. Try Chrome or Edge.
            </p>
        </div>

        <div v-if="userTranscript" class="results-container">
            <h2>Your Pronunciation (Detected Text):</h2>
            <p class="user-transcript">{{ userTranscript }}</p>
        </div>

        <div v-if="score !== null" class="results-container">
            <h2>Results:</h2>
            <p>Correct Words: {{ correctWordsCount }}</p>
            <p>Incorrect/Missed Words: {{ incorrectWordsCount }}</p>
            <p>Error Rate: {{ (errorRate * 100).toFixed(2) }}%</p>
            <p class="score">Score: {{ score.toFixed(2) }} / 100</p>
        </div>

        <div v-if="recognitionError" class="alert alert-danger mt-3">
            Error: {{ recognitionError }}
        </div>
    </div>
</template>

<script>
import * as Diff from 'diff'; // npm install diff

export default {
    name: 'App',
    data() {
        return {
            referenceText: "Hello world this is a simple test for read aloud practice.",
            // referenceText: "The quick brown fox jumps over the lazy dog.",
            isRecognizing: false,
            userTranscript: '',
            recognitionError: null,
            score: null,
            speechRecognition: null,
            isSpeechRecognitionSupported: true,

            displayWords: [], // Array of { text: 'word', status: 'pending' | 'correct' | 'incorrect' }
            correctWordsCount: 0,
            incorrectWordsCount: 0,
            errorRate: 0,
        };
    },
    computed: {
        originalWordsArray() {
            return this.tokenize(this.referenceText);
        },
        totalOriginalWords() {
            return this.originalWordsArray.length;
        }
    },
    created() {
        this.initializeDisplayWords();
        this.setupSpeechRecognition();
    },
    methods: {
        initializeDisplayWords() {
            this.displayWords = this.originalWordsArray.map(word => ({
                text: word,
                status: 'pending', // pending, correct, incorrect
            }));
            this.userTranscript = '';
            this.score = null;
            this.correctWordsCount = 0;
            this.incorrectWordsCount = 0;
            this.errorRate = 0;
        },

        tokenize(text) {
            if (!text) return [];
            return text.toLowerCase().replace(/[^\w\s']/g, "").replace(/\s+/g, ' ').trim().split(' ');
        },

        setupSpeechRecognition() {
            const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognitionAPI) {
                this.isSpeechRecognitionSupported = false;
                this.recognitionError = "Speech Recognition API is not supported in this browser.";
                console.error("Speech Recognition API not supported.");
                return;
            }

            this.speechRecognition = new SpeechRecognitionAPI();
            this.speechRecognition.continuous = true; // Keep listening
            this.speechRecognition.interimResults = true; // Get results as they come
            this.speechRecognition.lang = 'en-US'; // Set language

            this.speechRecognition.onstart = () => {
                this.isRecognizing = true;
                this.recognitionError = null;
                console.log('Speech recognition started');
            };

            this.speechRecognition.onresult = (event) => {
                let interimTranscript = '';
                let finalTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }
                this.userTranscript = finalTranscript.trim() || interimTranscript.trim(); // Show interim if final is not yet available
                // For immediate feedback while speaking, you could compare here too,
                // but it's often better to wait for the final transcript for accuracy.
            };

            this.speechRecognition.onerror = (event) => {
                this.isRecognizing = false;
                this.recognitionError = `Speech recognition error: ${event.error}`;
                if (event.error === 'no-speech') {
                    this.recognitionError = 'No speech was detected. Please try again.';
                } else if (event.error === 'audio-capture') {
                    this.recognitionError = 'Microphone problem. Ensure it is enabled and permissions are granted.';
                } else if (event.error === 'not-allowed') {
                    this.recognitionError = 'Permission to use microphone was denied. Please enable it in browser settings.';
                }
                console.error('Speech recognition error:', event);
                this.stopRecognitionInternally(); // Ensure it's stopped
            };

            this.speechRecognition.onend = () => {
                // This onend fires even if stopRecognition is called.
                // So, we only process if it wasn't an intentional stop followed by immediate processing.
                if (this.isRecognizing) { // If it ended unexpectedly
                    this.isRecognizing = false;
                    console.log('Speech recognition ended unexpectedly.');
                    if (this.userTranscript) {
                        this.processResults();
                    }
                }
                // If `stopRecognition` was called, `isRecognizing` would be false,
                // and `processResults` would have been called from `stopRecognition`.
            };
        },

        async startRecognition() {
            if (!this.isSpeechRecognitionSupported || !this.speechRecognition) return;
            this.initializeDisplayWords(); // Reset for a new attempt

            try {
                // Check for microphone permission (some browsers require explicit interaction before this check)
                await navigator.mediaDevices.getUserMedia({ audio: true }); // Request permission
                this.speechRecognition.start();
            } catch (err) {
                this.recognitionError = "Could not access microphone. Please grant permission.";
                console.error("Error accessing microphone:", err);
                this.isRecognizing = false;
            }
        },

        stopRecognition() {
            if (!this.isSpeechRecognitionSupported || !this.speechRecognition || !this.isRecognizing) return;
            this.speechRecognition.stop();
            this.isRecognizing = false; // Set this immediately
            console.log('Speech recognition stopped by user.');
            // Process results after a short delay to allow final transcript to settle
            setTimeout(() => {
                if (this.userTranscript) {
                    this.processResults();
                } else {
                    // Handle case where nothing was transcribed
                    this.recognitionError = "No speech was transcribed.";
                    this.initializeDisplayWords(); // Reset display
                }
            }, 200); // Adjust delay if needed
        },

        stopRecognitionInternally() {
            // Used by onerror to ensure the recognition process is halted
            if (this.speechRecognition && this.isRecognizing) {
                this.speechRecognition.stop();
                this.isRecognizing = false;
            }
        },

        processResults() {
            const originalWords = this.originalWordsArray;
            const spokenWords = this.tokenize(this.userTranscript);

            console.log("Original:", originalWords);
            console.log("Spoken:", spokenWords);

            const diffs = Diff.diffArrays(originalWords, spokenWords, {
                comparator: (left, right) => left === right // Simple string comparison
            });

            console.log("Diffs:", diffs);

            let newDisplayWords = [];
            let Sidx = 0; // Spoken words index
            let Oidx = 0; // Original words index (implicit via diff)

            this.correctWordsCount = 0;
            this.incorrectWordsCount = 0;

            diffs.forEach(part => {
                if (part.added) { // User said extra words - counts as error for overall accuracy
                    // These words are not in the original text, so they don't directly map to highlighting.
                    // We could count them as errors, but the primary goal is to see how well the *original* text was read.
                    // For scoring, each added word can be considered an error against the flow.
                    // This example focuses on errors in *reading the given text*.
                } else if (part.removed) { // Words in original, but not spoken (or mispronounced enough to be different)
                    part.value.forEach(word => {
                        newDisplayWords.push({ text: word, status: 'incorrect' });
                        this.incorrectWordsCount++;
                    });
                } else { // Common part
                    part.value.forEach(word => {
                        newDisplayWords.push({ text: word, status: 'correct' });
                        this.correctWordsCount++;
                    });
                }
            });

            // Ensure displayWords covers all original words, even if user spoke less
            // The diff should inherently handle this by showing 'removed' parts for trailing original words if user stopped early.
            this.displayWords = newDisplayWords;

            // If the diff algorithm doesn't fully align with original word count (e.g., if spoken text is much shorter)
            // we might need to adjust `incorrectWordsCount` based on the `totalOriginalWords`.
            // The `diffArrays` method should produce parts that sum up to the length of the longer array if one is a subsequence of another,
            // or a combined length otherwise.
            // For our scoring: an error is a word from the original text that was NOT marked 'correct'.
            this.incorrectWordsCount = this.totalOriginalWords - this.correctWordsCount;


            if (this.totalOriginalWords > 0) {
                this.errorRate = this.incorrectWordsCount / this.totalOriginalWords;
                this.score = (1 - this.errorRate) * 100;
            } else {
                this.errorRate = 0;
                this.score = 100; // Or 0 if empty text is an issue
            }
        },

        getWordClass(word) {
            if (word.status === 'correct') {
                return 'correct-word';
            } else if (word.status === 'incorrect') {
                return 'incorrect-word';
            }
            return 'pending-word';
        },
    },
    beforeUnmount() {
        if (this.speechRecognition) {
            this.speechRecognition.stop();
            this.speechRecognition.onstart = null;
            this.speechRecognition.onresult = null;
            this.speechRecognition.onerror = null;
            this.speechRecognition.onend = null;
        }
    }
};
</script>

<style>
body {
    font-family: sans-serif;
    line-height: 1.6;
    background-color: #f4f7f6;
    color: #333;
}

.container {
    max-width: 800px;
    margin: 20px auto;
    padding: 25px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h1,
h2 {
    color: #2c3e50;
    margin-bottom: 0.8em;
}

h1 {
    text-align: center;
    margin-bottom: 1.2em;
}

.reference-text-container,
.controls,
.results-container {
    margin-bottom: 25px;
    padding: 15px;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
}

.reference-text span {
    display: inline-block;
    /* Allows margin/padding if needed and prevents breaking mid-word highlight */
    margin-right: 0.1em;
    /* Tiny space after word before punctuation, if any */
    transition: background-color 0.3s, color 0.3s;
}

.pending-word {
    /* Default style */
}

.correct-word {
    color: #27ae60;
    /* Green */
    font-weight: bold;
}

.incorrect-word {
    color: #c0392b;
    /* Red */
    background-color: #fdd;
    text-decoration: line-through;
    font-weight: bold;
}

.btn {
    padding: 10px 18px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
    margin-right: 10px;
    transition: background-color 0.2s;
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.btn-primary {
    background-color: #3498db;
    color: white;
}

.btn-primary:hover:not(:disabled) {
    background-color: #2980b9;
}

.btn-danger {
    background-color: #e74c3c;
    color: white;
}

.btn-danger:hover:not(:disabled) {
    background-color: #c0392b;
}

.user-transcript {
    font-style: italic;
    color: #555;
    background-color: #f9f9f9;
    padding: 10px;
    border-radius: 4px;
    border: 1px dashed #ccc;
}

.score {
    font-size: 1.5em;
    font-weight: bold;
    color: #3498db;
}

.alert {
    padding: 15px;
    border-radius: 4px;
    margin-top: 20px;
}

.alert-danger {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.text-danger {
    color: #c0392b;
    font-size: 0.9em;
}
</style>