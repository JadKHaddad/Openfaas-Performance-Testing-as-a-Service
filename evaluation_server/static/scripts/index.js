const app = Vue.createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            hostname: location.hostname,
            socket: io(),
            id: null,
            ready: false,
            firstQuestions: [
                { q: "Wie lange programmieren Sie?", a: "1 Jahr", options: ["1 Jahr", "2 Jahre", "3 Jahre", "4 Jahre", "5 Jahre", "Über 5 Jahre"]},
                { q: "Wie oft programmieren Sie?", a: "Sehr selten", options: ["Sehr selten", "Selten", "Nicht oft", "Oft", "Regelmäßig", "Täglich"]},
                { q: "Ist Linux Ihr Hauptbetriebssystem?", a: "Ja", options: ["Ja", "Nein"]},
                { q: "Wie vertraut sind Sie mit der Kommandozeile? Auf einer Skala von 1 bis 10 ( je größer umso vertrauter )", a: "1", options: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] },
                { q: "Wie oft benutzen Sie die Kommandozeile?", a: "Sehr selten" , options: ["Sehr selten", "Selten", "Nicht oft", "Oft", "Regelmäßig", "Täglich"]},
            ],
            lastQuestions: [
                { q: "Ist das alte System im Allgemeinen einfach zu bedienen?", a: "Ja", options: ["Ja", "Teilweise", "Nein"]},
                { q: "Ist das neue System im Allgemeinen einfach zu bedienen?",  a: "Ja", options: ["Ja", "Teilweise", "Nein"]},
                { q: "Welche Schwierigkeiten hatten Sie mit dem alten System?", a: "" },
                { q: "Welche Schwierigkeiten hatten Sie mit dem neuen System?", a: "" },
                { q: "Können Sie die Aufgaben alleine wiederholen (altes System)", a: "Ja", options: ["Ja", "Teilweise", "Nein"] },
                { q: "Können Sie die Aufgaben alleine wiederholen (nues System)", a: "Ja", options: ["Ja", "Teilweise", "Nein"] },
                { q: "Mit welchem System würden Sie schneller arbeiten", a: "Mit dem alten System", options: ["Mit dem alten System", "Mit dem neuen System"] },
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