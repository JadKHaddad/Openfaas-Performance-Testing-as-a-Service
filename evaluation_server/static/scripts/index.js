const app = Vue.createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            hostname: location.hostname,
            socket: io(),
            id: null,
            ready: false,
            firstQuestions: [
                { q: "Wie lange programmieren Sie?", a: "" },
                { q: "Wie oft programmieren Sie?", a: "" },
                { q: "Ist Linux Ihr Hauptbetriebssystem?", a: "" },
                { q: "Wie vertraut sind Sie mit der Kommandozeile?", a: "" },
                { q: "Wie oft benutzen Sie die Kommandozeile?", a: "" },
            ],
            lastQuestions: [
                { q: "Ist das alte System im allgemeinen einfach zu bedienen?", a: "" },
                { q: "Ist das neue System im allgemeinen einfach zu bedienen?", a: "" },
                { q: "Welche Schwierigkeiten hatten Sie mit dem alten System?", a: "" },
                { q: "Welche Schwierigkeiten hatten Sie mit dem neuen System?", a: "" },
                { q: "Können Sie die Aufgaben alleine wiederholen (altes System)", a: "" },
                { q: "Können Sie die Aufgaben alleine wiederholen (nues System)", a: "" },
                { q: "Mit welchem System w ̈urden Sie schneller arbeiten", a: "" },
                { q: "Welches System würden Sie lieber benutzen? gibt es Fälle, in denen Sie das andere System benutzen würden? wenn ja, welche?", a: "" },
                { q: "Weitere Kommentare", a: "" },
                
            ],
            started: false,
            loading: false,
            username: "",
            password: "",
            port: "",
            ip: "",
            url: "",
            finished: false,
        }
    },
    methods: {
        start() {
            this.started = true;
            this.loading = true;
            fetch('/start', { method: "POST", headers: new Headers({'id': this.id}),})
                .then((data) => data.json())
                .then((data) => {
                    if (data.success){
                        this.username = data.username;
                        this.password = data.password;
                        this.port = data.port;
                        this.ip = data.ip;
                        this.url = `http://${this.ip}:${this.port}`
                    }
                })
                .catch((e) => {
                    console.log(e)
                }).finally(() => {
                    this.loading = false;
                });
        },
        submit() {
            fetch('/finish', { method: "POST", body: JSON.stringify({f:this.firstQuestions,l:this.lastQuestions}), headers: new Headers({'id': this.id}),})
                .then((data) => data.json())
                .then((data) => {
                    if (data.success){
                        this.finished = true;
                    }
                })
                .catch((e) => {
                    console.log(e)
                }).finally(() => {
                });
        }
    },
    created() {
        this.socket.on("id", (msg) => {
            this.id = msg.id;
        })
        this.socket.on("connect", () => {
            this.ready = true;
        });
    },
    mounted() {

    }
})
app.mount('#app')