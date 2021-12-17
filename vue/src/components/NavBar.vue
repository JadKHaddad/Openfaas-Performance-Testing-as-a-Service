<template>
  <div>
    <header>
      <!-- Navbar -->
      <nav class="navbar navbar-expand-lg navbar-light bg-white fixed-top">
        <div class="container-fluid">
          <button
            class="navbar-toggler"
            type="button"
            data-mdb-toggle="collapse"
            data-mdb-target="#navbarTop"
            aria-controls="navbarTop"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <i class="fas fa-bars"></i>
          </button>
          <div class="collapse navbar-collapse" id="navbarTop">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
              <li class="nav-item active">
                <router-link to="/" class="nav-link" aria-current="page"
                  >Home</router-link
                >
              </li>
              <li class="nav-item active">
                <router-link to="/control" class="nav-link" aria-current="page"
                  >Control</router-link
                >
                <!-- <a class="nav-link" aria-current="page" href="/control">Control</a> -->
              </li>
              <li class="nav-item">
                <router-link to="/license" class="nav-link" aria-current="page"
                  >License</router-link
                >
                <!-- <a class="nav-link" aria-current="page" href="/license" >License</a> -->
              </li>
              <li class="nav-item">
                <a
                  class="nav-link"
                  aria-current="page"
                  href="https://github.com/JadKHaddad/Openfaas-Performance-Testing-as-a-Service"
                  >Source</a
                >
              </li>
              <li class="nav-item">
                <router-link to="/openfaas" class="nav-link" aria-current="page"
                  >OpenFaaS</router-link
                >
                <!-- <a class="nav-link" aria-current="page" href="/openfaas">OpenFaaS</a> -->
              </li>
              <li class="nav-item">
                <a
                  @click="setUp"
                  class="nav-link"
                  aria-current="page"
                  id="nav-url"
                  href="#"
                  data-mdb-toggle="modal"
                  data-mdb-target="#Url-Modal"
                  ><i class="fas fa-cog" id="gear"></i>
                  <label id="url" style="font-weight: bold">
                    &nbsp;{{ openfaasUrl }}
                  </label></a
                >
              </li>
            </ul>
          </div>
        </div>
      </nav>
      <!-- Navbar -->
    </header>
    <!-- Url-Modal -->
    <div
      class="modal fade"
      id="Url-Modal"
      tabindex="-1"
      aria-labelledby="ModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-body">
            <form>
              <!-- input -->
              <div class="form-outline mb-4">
                <input
                  type="text"
                  id="url-input"
                  class="form-control"
                  v-model="tempOpenfaasUrl"
                  :disabled="tempNoOpenfaas"
                />
                <label class="form-label" for="url-input">OpenFaaS url</label>
              </div>
              <!-- checkbox -->
              <div
                class="form-check"
                data-mdb-toggle="tooltip"
                title="Can the brwoser connect to OpenFaas directly?"
              >
                <input
                  class="form-check-input"
                  type="checkbox"
                  value=""
                  id="direct-checkbox"
                  v-model="tempDirect"
                  :disabled="tempNoOpenfaas"
                />
                <label class="form-check-label" for="direct-checkbox">
                  Direct connection
                </label>
              </div>
              <!-- checkbox -->
              <div
                class="form-check"
                data-mdb-toggle="tooltip"
                title="No OpenFaaS-Server is being used"
              >
                <input
                  class="form-check-input"
                  type="checkbox"
                  value=""
                  id="no-openfaas-checkbox"
                  v-model="tempNoOpenfaas"
                />
                <label class="form-check-label" for="no-openfaas-checkbox">
                  No OpenFaaS
                </label>
              </div>
              <!-- checkbox -->
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  value=""
                  id="dark-theme-checkbox"
                  v-model="tempDarkTheme"
                />
                <label class="form-check-label" for="dark-theme-checkbox">
                  Dark theme
                </label>
              </div>
              <!-- checkbox -->
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  value=""
                  id="i-do-not-like-rounded-edges-checkbox"
                  v-model="tempNoRedges"
                />
                <label
                  class="form-check-label"
                  for="i-do-not-like-rounded-edges-checkbox"
                >
                  I don't like rounded edges
                </label>
              </div>
              <!-- checkbox -->
              <div
                class="form-check"
                data-mdb-toggle="tooltip"
                title="Tests will be minimized by default"
              >
                <input
                  class="form-check-input"
                  type="checkbox"
                  value=""
                  id="minimized"
                  v-model="tempMinimizeTests"
                />
                <label class="form-check-label" for="minimized">
                  Minimize tests
                </label>
              </div>
              <div>
                <label v-if="error" id="url-message"
                  >Could not connect to openfaas</label
                >
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <div
              v-if="loading"
              class="spinner-border text-primary spinner"
              id="url-spinner"
            ></div>
            <button
              type="button"
              class="btn btn-danger"
              id="restore-defaults-btn"
              @click="restoreDefault"
              :disabled="loading"
            >
              Restore defaults
            </button>
            <button
              type="button"
              class="btn btn-primary"
              id="set-url-btn"
              @click="ok"
              :disabled="loading"
            >
              Ok
            </button>
          </div>
          <button
            type="button"
            class="btn btn-primary hidden"
            data-mdb-dismiss="modal"
            id="dismiss-url-modal-btn"
            ref="dismissBtn"
          ></button>
        </div>
      </div>
    </div>
    <!-- Button trigger Url modal -->
    <div>
      <button
        type="button"
        class="btn btn-primary hidden"
        data-mdb-toggle="modal"
        data-mdb-target="#Url-Modal"
        id="url-modal-button"
      ></button>
    </div>
    <div id="server-stats">
      Running tests: <label id="running-tests-label"> {{ runningTests }}</label>
    </div>
  </div>
</template>

<script>
export default {
  name: "NavBar",
  props: [
    "runningTests",
    "openfaasUrl",
    "direct",
    "noOpenfaas",
    "functionName",
    "minimizeTests",
    "darkTheme",
    "noRedges",
  ],
  data() {
    return {
      tempOpenfaasUrl: "None",
      tempDirect: null,
      tempNoOpenfaas: null,
      tempDarkTheme: null,
      tempNoRedges: null,
      tempMinimizeTests: null,

      loading: false,
      error: false,
    };
  },

  methods: {
    setUp() {
      if (!this.noOpenfaas) this.tempOpenfaasUrl = this.openfaasUrl;
      this.tempDirect = this.direct;
      this.tempNoOpenfaas = this.noOpenfaas;
      this.tempDarkTheme = this.darkTheme;
      this.tempNoRedges = this.noRedges;
      this.tempMinimizeTests = this.minimizeTests;
      this.error = false;
    },
    restoreDefault() {
      this.loading = true;
      this.error = false;
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
          this.$refs.dismissBtn.click();
          console.log(settings)
          this.$emit("default", settings);
        })
        .catch(() => {
          this.$refs.dismissBtn.click();
          this.loading = false;
          this.error = true;
        });
    },
    ok() {
      var onSuccess = (newOpenfaasurl, newBaseUrl) => {
        var settings = {
          baseUrl: newBaseUrl,
          openfaasUrl: newOpenfaasurl,
          direct: this.tempDirect,
          noOpenfaas: this.tempNoOpenfaas,
          darkTheme: this.tempDarkTheme,
          noRedges: this.tempNoRedges,
          minimizeTests: this.tempMinimizeTests,
        };
        this.loading = false;
        this.error = false;
        this.$refs.dismissBtn.click();
        this.$emit("settings", settings);
        //dismiss
      };

      //calculate
      if (!this.tempNoOpenfaas) {
        var newOpenfaasurl = this.tempOpenfaasUrl;
        newOpenfaasurl = newOpenfaasurl
          .replace("http://", "")
          .replace("https://", "");
        newOpenfaasurl = "http://" + newOpenfaasurl;
        //check if this url works
        this.loading = true;
        this.error = false;
        fetch("/check_connection", {
          method: "POST",
          body: JSON.stringify({ url: newOpenfaasurl }),
        })
          .then((data) => data.json())
          .then((data) => {
            if (data.success) {
              if (newOpenfaasurl.slice(-1) == "/") {
                newOpenfaasurl = newOpenfaasurl.slice(0, -1);
              }

              var newBaseUrl = `${newOpenfaasurl}/function/ptas`;
              if (!this.tempDirect) newBaseUrl = "/proxy";
              onSuccess(newOpenfaasurl, newBaseUrl);
            } else {
              this.loading = false;
              this.error = true;
            }
          })
          .catch(() => {
            this.loading = false;
            this.$root.showInfo("Could not connect to server", "red");
          });
      } else {
        onSuccess("None", "/local");
      }
    },
  },

  created() {
    this.setUp();
  },
  mounted() {
    // rotate element
    $.fn.animateRotate = function (angle, duration, easing, complete) {
      var args = $.speed(duration, easing, complete);
      var step = args.step;
      return this.each(function (i, e) {
        args.complete = $.proxy(args.complete, e);
        args.step = function (now) {
          $.style(e, "transform", "rotate(" + now + "deg)");
          if (step) return step.apply(e, arguments);
        };

        $({ deg: 0 }).animate({ deg: angle }, args);
      });
    };

    $("#nav-url").on("click", () => {
      $("#gear").animateRotate(180);
      $("*").bind("click.myEvents", (event) => {
        if (event.currentTarget == $("#Url-Modal")[0]) {
          $("#gear").animateRotate(-180);
          $("*").off(".myEvents");
        }
        event.stopPropagation();
      });
      return false;
    });
  },
};
</script>

