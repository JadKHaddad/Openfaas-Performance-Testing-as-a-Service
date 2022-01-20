<template>
  <div>
    <div :id="id">
      <div class="test-container">
        <div class="buttons btn-container">
          <button
            type="button"
            class="btn btn-primary stop-test"
            @click="stop"
            :disabled="!running"
          >
            Stop
          </button>
          <button
            type="button"
            class="btn btn-primary restart-test"
            @click="restart"
            :disabled="running"
          >
            Restart
          </button>
          <button
            type="button"
            class="btn btn-primary download-test"
            @click="download"
            :disabled="running"
          >
            Download
          </button>
          <button
            type="button"
            class="btn btn-primary show-test-results"
            @click="showResults"
            :disabled="!showResultsComp || !valid"
          >
            {{ resultsText }}
          </button>
          <button
            type="button"
            class="btn btn-danger delete-test"
            @click="deleteMe"
          >
            Delete
          </button>
        </div>
        <div v-if="showResultsBool" class="img-container">
          <img class="lin" :src="linImageUrl" />
          <img class="reg" :src="regImageUrl" />
        </div>
        <div v-if="showPath" class="path">
          <router-link :to="{ name: 'Project', params: { id: pid } }">
            {{ pid }}
          </router-link>
          &nbsp;&nbsp;
          <i class="fas fa-angle-right"></i>
          &nbsp;&nbsp;
          <router-link :to="{ name: 'Script', params: { pid: pid, id: sid } }">
            {{ sid }}
          </router-link>
        </div>

        <div
          class="card"
          data-mdb-toggle="tooltip"
          :title="tooltipText"
          @dblclick="minimize"
        >
          <div class="card-header">
            <div v-if="info.description" class="description" data-mdb-toggle="tooltip" title="Description">{{ info.description }}</div>
            <div class="row">
              <div
                class="col-3 test-id"
                :class="{ green: running, red: !valid }"
              >
                <label data-mdb-toggle="tooltip" title="Test id">{{
                  id
                }}</label>
              </div>
              <div class="col-1" data-mdb-toggle="tooltip" title="Users">
                <i class="fas fa-user-alt"></i> {{ info.users }}
              </div>
              <div class="col-1" data-mdb-toggle="tooltip" title="Spawn rate">
                <i class="fas fa-users"></i> {{ info.spawn_rate }}
              </div>
              <div class="col-1" data-mdb-toggle="tooltip" title="Workers">
                <i class="fas fa-hard-hat"></i> {{ workers }}
              </div>
              <div class="col-3" data-mdb-toggle="tooltip" title="Host">
                <i class="fas fa-globe"></i> {{ info.host }}
              </div>
              <div
                class="col-1"
                data-mdb-toggle="tooltip"
                title="Time is seconds"
              >
                <i class="fas fa-clock"></i>
                {{ info.time }}
              </div>
              <div
                class="col-1 elapsed"
                data-mdb-toggle="tooltip"
                title="Elapsed time is seconds"
                v-if="running"
              >
                <i class="fas fa-stopwatch"></i>
                <label class="elapsed-text">&nbsp;{{ elapsed }}</label>
              </div>
              <div class="col-1">
                <div
                  v-if="running"
                  class="spinner-border text-primary spinner"
                  data-mdb-toggle="tooltip"
                  title="Running"
                ></div>
                <i v-if="showCheck" class="fas fa-check check" data-mdb-toggle="tooltip" title="Done"></i>
                <i v-if="showX" class="fas fa-times not-valid" data-mdb-toggle="tooltip" title="Not valid"></i>
              </div>
            </div>
          </div>
          <div
            class="card-body"
            ref="cardBody"
            :style="startMinimized ? 'display: none;' : 'display: block;'"
          >
            <div class="container-fluid">
              <div class="row">
                <div class="col-1">Type</div>
                <div class="col-2">Name</div>
                <div class="col-1">Requests</div>
                <div class="col-1">Fails</div>
                <div class="col-1">Med</div>
                <div class="col-1">Avg (ms)</div>
                <div class="col-1">Min (ms)</div>
                <div class="col-1">Max (ms)</div>
                <div class="col-1">Avg size (bytes)</div>
                <div class="col-1">RPS</div>
                <div class="col-1">FPS</div>
              </div>
            </div>
            <div v-if="renderData" class="container-fluid results">
              <div v-for="d in data.slice(0, -1)" :key="d" class="row">
                <div class="col-1">{{ d["Type"] }}</div>
                <div class="col-2">{{ d["Name"] }}</div>
                <div class="col-1">{{ d["Request Count"] }}</div>
                <div class="col-1">{{ d["Failure Count"] }}</div>
                <div class="col-1">{{ d["Median Response Time"] }}</div>
                <div class="col-1">
                  {{ d["Average Response Time"].toString().slice(0, 8) }}
                </div>
                <div class="col-1">
                  {{ d["Min Response Time"].toString().slice(0, 8) }}
                </div>
                <div class="col-1">
                  {{ d["Max Response Time"].toString().slice(0, 8) }}
                </div>
                <div class="col-1">
                  {{ d["Average Content Size"].toString().slice(0, 8) }}
                </div>
                <div class="col-1">
                  {{ d["Requests/s"].toString().slice(0, 8) }}
                </div>
                <div class="col-1">
                  {{ d["Failures/s"].toString().slice(0, 8) }}
                </div>
              </div>
            </div>
          </div>
          <div v-if="renderData" class="card-footer">
            <div class="row">
              <div class="col-1"></div>
              <div class="col-2">{{ data.at(-1)["Name"] }}</div>
              <div class="col-1">{{ data.at(-1)["Request Count"] }}</div>
              <div class="col-1">{{ data.at(-1)["Failure Count"] }}</div>
              <div class="col-1">{{ data.at(-1)["Median Response Time"] }}</div>
              <div class="col-1">
                {{
                  data.at(-1)["Average Response Time"].toString().slice(0, 8)
                }}
              </div>
              <div class="col-1">
                {{ data.at(-1)["Min Response Time"].toString().slice(0, 8) }}
              </div>
              <div class="col-1">
                {{ data.at(-1)["Max Response Time"].toString().slice(0, 8) }}
              </div>
              <div class="col-1">
                {{ data.at(-1)["Average Content Size"].toString().slice(0, 8) }}
              </div>
              <div class="col-1">
                {{ data.at(-1)["Requests/s"].toString().slice(0, 8) }}
              </div>
              <div class="col-1">
                {{ data.at(-1)["Failures/s"].toString().slice(0, 8) }}
              </div>
            </div>
          </div>
        </div>
        
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Test",
  props: [
    "test",
    "showPath",
    "url",
    "openfaasUrl",
    "pid",
    "sid",
    "startMinimized",
    "info",
    "data",
    "status",
    "valid",
    "id",
  ],
  data() {
    return {
      running: false,
      elapsed: "",
      elapsedIntv: null,
      enoughData: true,
      showResultsBool: false,
      linImageUrl: "",
      regImageUrl: "",
      dataLoaded: false,
      resultsText: "Show results",
      loadingImages: false,
      minimized: false,
      tooltipText: "Double click to minimize",
      workers: "",
    };
  },
  computed: {
    showCheck() {
      return !this.running && this.valid;
    },
    showX() {
      return !this.running && !this.valid;
    },
    renderData() {
      if (this.data != null) return this.data.length > 0;
      else return false;
    },
    showResultsComp() {
      return this.enoughData && !this.running && !this.loadingImages;
    },
  },
  methods: {
    minimize() {
      if (this.minimized) {
        this.tooltipText = "Double click to minimize";
      } else {
        this.tooltipText = "Double click to maximize";
      }
      $(this.$refs.cardBody).slideToggle();
      this.minimized = !this.minimized;
    },
    stop() {
      fetch(this.url, {
        method: "POST",
        body: JSON.stringify({
          command: 8,
          project_name: this.pid,
          script_name: this.sid,
          id: this.id,
        }),
      })
        .then((data) => data.json())
        .then((data) => {
          if (data.success) {
            this.running = false;
            this.$emit("stop");
          } else {
            this.$root.showInfo("There was an error stopping the test", "red");
          }
        })
        .catch(() => {
          this.$root.showInfo("Could not connect to server", "red");
        });
    },
    restart() {
      this.$emit("restart", this.info, this.pid, this.sid);
    },
    deleteMe() {
      this.$root.setUpConfirmation(
        this.id + ": Are you sure you want to delete this test?",
        "Delete",
        () => {
          fetch(this.url, {
            method: "POST",
            body: JSON.stringify({
              command: 9,
              project_name: this.pid,
              script_name: this.sid,
              id: this.id,
            }),
          })
            .then((data) => data.json())
            .then((data) => {
              if (data.success) {
                this.$emit("delete", this.id, this.pid, this.sid);
              } else {
                this.$root.showInfo(
                  "There was an error deleting the test",
                  "red"
                );
              }
            })
            .catch(() => {
              this.$root.showInfo("Could not connect to server", "red");
            });
        }
      );
    },
    download() {
      fetch(this.url, {
        method: "POST",
        body: JSON.stringify({
          command: 11,
          project_name: this.pid,
          script_name: this.sid,
          id: this.id,
        }),
      })
        .then((response) => response.blob())
        .then((blob) => {
          var objectUrl = URL.createObjectURL(blob);
          window.location.href = objectUrl;
        });
    },
    showResults() {
      if (this.dataLoaded) {
        if (this.showResultsBool) {
          this.resultsText = "Show results";
        } else {
          this.resultsText = "Hide results";
        }
        this.showResultsBool = !this.showResultsBool;
      } else {
        this.loadingImages = true;
        fetch(this.url, {
          method: "POST",
          body: JSON.stringify({
            command: 12,
            project_name: this.pid,
            script_name: this.sid,
            id: this.id,
            type: 1,
          }),
        })
          .then((data) => data.json())
          .then((data) => {
            if (data.success) {
              if (data.status_code == 0) {
                fetch(this.url, {
                  method: "POST",
                  body: JSON.stringify({
                    command: 12,
                    project_name: this.pid,
                    script_name: this.sid,
                    id: this.id,
                    type: 2,
                  }),
                })
                  .then((response) => response.blob())
                  .then((blob) => {
                    var urlCreator = window.URL || window.webkitURL;
                    this.linImageUrl = urlCreator.createObjectURL(blob);
                    fetch(this.url, {
                      method: "POST",
                      body: JSON.stringify({
                        command: 12,
                        project_name: this.pid,
                        script_name: this.sid,
                        id: this.id,
                        type: 3,
                      }),
                    })
                      .then((response) => response.blob())
                      .then((blob) => {
                        var urlCreator = window.URL || window.webkitURL;
                        this.regImageUrl = urlCreator.createObjectURL(blob);
                        this.resultsText = "Hide results";
                        //show results
                        this.showResultsBool = true;
                        this.dataLoaded = true;
                      });
                  });
              } else if (data.status_code == 2) {
                // console.log("not enof");
                this.$root.showInfo("Not enough data to analyse", "red");
                this.showResultsBool = false;
                this.enoughData = false;
              }
            }
            this.loadingImages = false;
          })
          .catch(() => {
            this.$root.showInfo("Could not connect to server", "red");
            this.loadingImages = false;
          });
      }
    },
  },
  created() {
    if(this.info.workers !== 0) this.workers = this.info.workers;
    this.minimized = this.startMinimized;
    if (this.minimized) this.tooltipText = "Double click to maximize";
  },
  beforeUnmount() {
    if (this.elapsedIntv) clearInterval(this.elapsedIntv);
  },
  updated() {
    if (!this.valid || this.status === 0) this.running = false;
  },
  mounted() {
    this.running = JSON.parse(this.status) === 1 ? true : false;
    if (this.running) {
      this.elapsed = parseInt(Date.now() / 1000 - this.info.started_at);
      this.elapsedIntv = setInterval(() => {
        this.elapsed = parseInt(Date.now() / 1000 - this.info.started_at);
      }, 1000);
    }
  },
};
</script>

<style>
</style>