<template>
  <div
    :class="{
      nr: noRedges,
      dark: darkTheme,
    }"
  >
    <NavBar
      :runningTests="runningTests"
      :openfaasUrl="openfaasUrl"
      :direct="direct"
      :noOpenfaas="noOpenfaas"
      :functionName="functionName"
      :minimizeTests="minimizeTests"
      :darkTheme="darkTheme"
      :noRedges="noRedges"
      :rollBack="navBarRollBack"
      @default="setDefaults"
      @settings="updateSettings"
      @rolledBack="setNavBarRollBack"
    />
    <router-view
      :url="url"
      :openfaasUrl="openfaasUrl"
      :socket="socket"
      :minimizeTests="minimizeTests"
      :update="update"
      @info="showInfo"
    />
    <!-- Button trigger info modal -->
    <div>
      <button
        type="button"
        class="btn btn-primary hidden"
        data-mdb-toggle="modal"
        data-mdb-target="#Info-Modal"
        id="info-modal-button"
        ref="infoModalButton"
      ></button>
    </div>

    <!-- Info Modal -->
    <div
      class="modal fade"
      id="Info-Modal"
      tabindex="-1"
      aria-labelledby="ModalLabel"
      aria-hidden="true"
      ref="infoModal"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-body info-message-container">
            <div>
              <label
                id="info-message"
                :class="{
                  green: infoColor === 'green',
                  red: infoColor === 'red',
                }"
                >{{ infoMessage }}</label
              >
            </div>
            <div v-if="infoError">
              <label id="info-error">{{ infoErrorText }}</label>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Button trigger confirmation modal -->
    <div>
      <button
        type="button"
        class="btn btn-primary hidden"
        data-mdb-toggle="modal"
        data-mdb-target="#Confirmation-Modal"
        id="confirmation-modal-button"
        ref="confirmationModalButton"
      ></button>
    </div>

    <!-- Confimation Modal -->
    <div
      class="modal fade"
      id="Confirmation-Modal"
      tabindex="-1"
      aria-labelledby="ModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-body">
            <h3 id="confirm-message"></h3>
            {{ confirmMessage }}
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-danger"
              data-mdb-dismiss="modal"
              ref="confirmBtn"
            >
              {{ confirmButtonText }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <teleport  to="#teleported">
      <div class="background-dark" :class="{dark: darkTheme}"></div>
    </teleport>
    <teleport to="#teleported-footer">
      <Footer
        :class="{
          dark: darkTheme,
          'bg-light': !darkTheme,
        }"
      />
    </teleport>
  </div>
</template>

<script>
import NavBar from "@/components/NavBar.vue";
import Footer from "@/components/Footer.vue";

export default {
  name: "App",
  components: {
    NavBar,
    Footer,
  },
  data() {
    return {
      openfaasUrl: "None",
      direct: true,
      noOpenfaas: true,
      functionName: "ptas",
      darkTheme: false,
      noRedges: false,
      minimizeTests: false,
      update: false,
      url: "/local",
      runningTests: 0,
      socket: null,
      infoMessage: "",
      infoColor: "green",
      infoError: true,
      infoErrorText: "",
      confirmMessage: "",
      confirmButtonText: "confirm",
      navBarRollBack: false,
    };
  },
  methods: {
    disconnect() {
      this.socket.off(this.openfaasUrl);
      console.log("disconnected from: " + this.openfaasUrl);
    },
    register() {
      this.socket.emit("register", { openfaasurl: this.openfaasUrl });
      this.socket.on(this.openfaasUrl, (msg) => {
        //console.log(msg)
        if (IsJsonString(msg)) {
          msg = JSON.parse(msg);
          if (msg.success) this.runningTests = msg.count;
        }
      });
      this.socket.on(this.openfaasUrl + "_clean_up", (msg) => {
        if (this.$route.name === "Project" || this.$route.name === "Script") {
          this.$router.push({ name: "Home" });
          this.showInfo("All projects deleted", "green");
        }
      });
      console.log("connected to: " + this.openfaasUrl);
    },
    configureConnections() {
      this.socket = io(process.env.VUE_APP_ROOT_API);
      this.socket.on("connect", () => this.register());
      console.log("current openfaasUrl: " + this.openfaasUrl);
      console.log("current baseUrl: " + this.url);
    },
    showInfo(message, color, error) {
      this.infoMessage = message;
      this.infoColor = color;
      if (error != null && error != "None") {
        this.infoError = true;
        this.infoErrorText = error;
      } else {
        this.infoError = false;
      }
      if (!$(this.$refs.infoModal).hasClass("show"))
        $(this.$refs.infoModalButton).click();
    },
    setUpConfirmation(message, btnText, func) {
      this.confirmMessage = message;
      this.confirmButtonText = btnText;
      $(this.$refs.confirmBtn).off("click").on("click", func);
      $(this.$refs.confirmationModalButton).click();
    },
    updateSettings(settings) {
      this.disconnect();
      this.url = settings.baseUrl;
      this.openfaasUrl = settings.openfaasUrl;
      this.direct = settings.direct;
      this.noOpenfaas = settings.noOpenfaas;
      this.darkTheme = settings.darkTheme;
      this.noRedges = settings.noRedges;
      this.minimizeTests = settings.minimizeTests;

      //localStorage.setItem("last_host", this.host);
      localStorage.setItem("url", this.url);
      localStorage.setItem("openfaasUrl", this.openfaasUrl);
      localStorage.setItem("direct", this.direct);
      localStorage.setItem("noOpenfaas", this.noOpenfaas);
      localStorage.setItem("darkTheme", this.darkTheme);
      localStorage.setItem("noRedges", this.noRedges);
      localStorage.setItem("minimizeTests", this.minimizeTests);
      this.update = true;
      this.register();
      this.navBarRollBack = true;
      console.log("new openfaasUrl: " + this.openfaasUrl);
      console.log("new baseUrl: " + this.url);
    },
    updated() {
      //console.log("updated");
      this.update = false;
    },
    setDefaults(settings) {
      this.disconnect();
      //console.log(settings);
      this.url = settings.baseUrl;
      this.openfaasUrl = settings.openfaasUrl;
      this.direct = settings.direct;
      this.noOpenfaas = settings.noOpenfaas;
      localStorage.setItem("url", this.url);
      localStorage.setItem("openfaasUrl", this.openfaasUrl);
      localStorage.setItem("direct", this.direct);
      localStorage.setItem("noOpenfaas", this.noOpenfaas);
      this.update = true;
      this.register();
      this.navBarRollBack = true;
      console.log("default openfaasUrl: " + this.openfaasUrl);
      console.log("default baseUrl: " + this.url);
    },
    setNavBarRollBack(){
      this.navBarRollBack = false;
    }
  },
  created() {
    if (localStorage.getItem("url")) this.url = localStorage.getItem("url");
    if (localStorage.getItem("openfaasUrl"))
      this.openfaasUrl = localStorage.getItem("openfaasUrl");
    if (localStorage.getItem("direct"))
      this.direct = JSON.parse(localStorage.getItem("direct"));
    if (localStorage.getItem("noOpenfaas"))
      this.noOpenfaas = JSON.parse(localStorage.getItem("noOpenfaas"));
    if (localStorage.getItem("darkTheme"))
      this.darkTheme = JSON.parse(localStorage.getItem("darkTheme"));
    if (localStorage.getItem("noRedges"))
      this.noRedges = JSON.parse(localStorage.getItem("noRedges"));
    if (localStorage.getItem("minimizeTests"))
      this.minimizeTests = JSON.parse(localStorage.getItem("minimizeTests"));
    if (
      !localStorage.getItem("url") ||
      !localStorage.getItem("openfaasUrl") ||
      !localStorage.getItem("direct")
    ) {
      console.log("no saved data found. restoring defaults..");
      fetch("/defaults", { method: "POST" })
        .then((data) => data.json())
        .then((data) => {
          if (data.openfaas_url) {
            this.tempNoOpenfaas = false;
            var newOpenfaasUrl = data.openfaas_url;
            if (newOpenfaasUrl.slice(-1) == "/") {
              newOpenfaasUrl = newOpenfaasUrl.slice(0, -1);
            }
            var newBaseUrl = `${newOpenfaasUrl}/function/ptas`;
            if (!data.direct) {
              newBaseUrl = "/proxy";
            }
          } else {
            newOpenfaasUrl = "None";
            newBaseUrl = "/local";
            this.tempNoOpenfaas = true;
          }
          this.tempDirect = data.direct;
          this.loading = false;
          var settings = {
            baseUrl: newBaseUrl,
            openfaasUrl: newOpenfaasUrl,
            direct: this.tempDirect,
            noOpenfaas: this.tempNoOpenfaas,
          };
          this.setDefaults(settings);
        })
        .catch(() => {
          this.showInfo("Could not connect to server", "red");
        });
    }
  },
  // updated(){
  //   console.log(this.socket._callbacks)
  // },
  mounted() {
    //mdb init
    document.querySelectorAll(".form-outline").forEach((formOutline) => {
      new mdb.Input(formOutline).init();
    });
    this.configureConnections();
  },
};
</script>

<style>
</style>
