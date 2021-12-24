<template>
  <div>
    <h3>{{ id }}</h3>
    <!-- Button trigger modal -->
    <div class="btn-container">
      <button
        type="button"
        class="btn btn-primary"
        data-mdb-toggle="modal"
        data-mdb-target="#Modal"
      >
        Start
      </button>
      <button
        type="button"
        class="btn btn-danger"
        id="stop-script-tests"
        @click="stopAll"
      >
        Stop all
      </button>
      <button
        type="button"
        class="btn btn-danger"
        id="delete-script-tests"
        @click="deleteAll"
      >
        Delete all
      </button>
    </div>
    <Test
      v-for="test in reversedTests"
      :key="test[0]"
      :id="test[0]"
      :info="JSON.parse(test[1].info)"
      :data="JSON.parse(test[1].data)"
      :status="test[1].status"
      :valid="test[1].valid"
      :showPath="false"
      :url="url"
      :openfaasUrl="openfaasUrl"
      :pid="pid"
      :sid="id"
      :startMinimized="minimizeTests"
      @restart="restart"
      @delete="deleteTest"
      @stop="stop(test[0])"
    ></Test>
    <!-- Modal -->
    <div
      class="modal fade"
      id="Modal"
      tabindex="-1"
      aria-labelledby="ModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="ModalLabel">Start</h5>
          </div>
          <div class="modal-body">
            <form>
              <!-- Users input -->
              <div class="form-outline mb-4">
                <input
                  type="text"
                  id="users-input"
                  class="form-control"
                  v-model="users"
                />
                <label class="form-label" for="users-input">Users</label>
              </div>
              <!-- Spawn rate input -->
              <div class="form-outline mb-4">
                <input
                  type="text"
                  id="spawn-rate-input"
                  class="form-control"
                  v-model="spawnRate"
                />
                <label class="form-label" for="spawn-rate-input"
                  >Spawn rate</label
                >
              </div>
              <!-- Workers input -->
              <div class="form-outline mb-4">
                <input
                  type="text"
                  id="workers-input"
                  class="form-control"
                  v-model="workers"
                />
                <label class="form-label" for="workers-input">Workers</label>
              </div>
              <div class="form-text" style="padding-bottom: 10px">
                This will overwrite all hosts in your file
              </div>
              <!-- Host input -->
              <div class="form-outline mb-4">
                <input
                  type="text"
                  id="host-input"
                  class="form-control"
                  v-model="host"
                />
                <label class="form-label" for="host-input">Host</label>
              </div>
              <div class="form-text" style="padding-bottom: 10px">
                If time is not set, the test will not stop automatically
              </div>
              <!-- Time input -->
              <div class="form-outline mb-4">
                <input
                  type="text"
                  id="time-input"
                  class="form-control"
                  v-model="time"
                />
                <label class="form-label" for="time-input"
                  >Time in seconds</label
                >
              </div>
              <!-- Submit button -->
              <button
                type="button"
                class="btn btn-primary btn-block"
                id="start-btn"
                @click="startFromModal"
              >
                Start
              </button>
            </form>
            <button
              type="button"
              class="btn btn-primary hidden"
              data-mdb-dismiss="modal"
              id="dismiss-btn"
              ref="dismiss"
            ></button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Test from "@/components/Test.vue";

export default {
  name: "Script",
  components: {
    Test,
  },
  props: ["url", "openfaasUrl", "socket", "minimizeTests", "update"],
  data() {
    return {
      id: this.$route.params.id,
      pid: this.$route.params.pid,
      tests: {},
      users: "",
      spawnRate: "",
      workers: "",
      host: "",
      time: "",
    };
  },
  methods: {
    register(test_ids) {
      this.socket.off(this.openfaasUrl + "_" + this.pid + "_" + this.id);
      this.socket.emit("register_script", {
        openfaasurl: this.openfaasUrl,
        project_name: this.pid,
        script_name: this.id,
        test_ids: test_ids,
      });
      this.socket.on(
        this.openfaasUrl + "_" + this.pid + "_" + this.id,
        (msg) => {
          if (IsJsonString(msg)) {
            msg = JSON.parse(msg);
            //console.log(msg);
            if (msg.success) {
              for (var i = 0; i < msg.tests.length; i++) {
                const id = msg.tests[i].id;
                if (id in this.tests) {
                  const status = msg.tests[i].status;
                  if (status === 0) {
                    // not running
                    this.disconnectTest(id);
                    this.tests[id].status = 0;
                  } else if (status === 1) {
                    this.tests[id].data = msg.tests[i].data;
                  } else if (status === 3) {
                    // console.log("not valid");
                    this.tests[id].valid = false;
                    this.$emit("info", id + ": There was an error running this test", "red");
                    this.disconnectTest(id);
                  }
                }
              }
            }
          }
        }
      );
      // console.log("script registered");
    },
    registerTest(test_id) {
      this.socket.emit("register_test", {
        openfaasurl: this.openfaasUrl,
        project_name: this.pid,
        script_name: this.id,
        test_id: test_id,
      });
    },
    disconnectTest(test_id) {
      // console.log("disconnecting");
      this.socket.emit("disconnect_test", {
        openfaasurl: this.openfaasUrl,
        project_name: this.pid,
        script_name: this.id,
        test_id: test_id,
      });
    },
    init() {
      //get host
      this.host = localStorage.getItem("last_host");
      //mdb init
      document.querySelectorAll(".form-outline").forEach((formOutline) => {
        new mdb.Input(formOutline).init();
      });
      fetch(this.url, {
        method: "POST",
        body: JSON.stringify({
          command: 7,
          project_name: this.pid,
          script_name: this.id,
        }),
      })
        .then((data) => data.json())
        .then((data) => {
          if (data.success) {
            //console.log(data)
            var test_ids = [];
            for (var test_id in data.tests) {
              if (data.tests[test_id].status === 1) {
                test_ids.push(data.tests[test_id].id);
              }
            }
            this.register(test_ids);
            // console.log("registering: ", test_ids);
            this.tests = data.tests;
          }
        })
        .catch((e) => {
          // console.log(e);
          this.$emit("info", "Could not connect to server", "red");
        });
      this.socket.on(
        this.openfaasUrl + "_" + this.pid + "_" + this.id + "_test_start",
        (msg) => {
          // console.log(msg.id in this.tests);
          if (msg.id in this.tests) return;
          this.tests[msg.id] = msg;
          this.registerTest(msg.id);
        }
      );
      this.socket.on(
        this.openfaasUrl + "_" + this.pid + "_" + this.id + "_test_delete",
        (msg) => {
          // console.log(msg);
          for (var i = 0; i < msg.length; i++) {
            if (msg[i] in this.tests) {
              delete this.tests[msg[i]];
              this.disconnectTest(msg[i]);
            }
          }
        }
      );
    },
    stopAll() {
      this.$root.setUpConfirmation(
        this.id + ": Are you sure you want to stop all tests?",
        "Stop",
        () => {
          fetch(this.url, {
            method: "POST",
            body: JSON.stringify({
              command: 17,
              project_name: this.pid,
              script_name: this.id,
            }),
          })
            .then((data) => data.json())
            .then((data) => {
              if (data.success) {
                this.$emit("info", "Success", "green");
                this.socket.emit("disconnect_script", {
                  project_name: this.pid,
                  script_name: this.id,
                });
                for (var key in this.tests) {
                  this.tests[key].status = 0;
                }
              } else {
                this.$emit("info", "There was an error stopping tests", "red");
              }
            })
            .catch(function () {
              this.$emit("info", "Could not connect to server", "red");
            });
        }
      );
    },
    deleteAll() {
      this.$root.setUpConfirmation(
        this.id + ": Are you sure you want to delete all tests?",
        "Delete",
        () => {
          fetch(this.url, {
            method: "POST",
            body: JSON.stringify({
              command: 16,
              project_name: this.pid,
              script_name: this.id,
            }),
          })
            .then((data) => data.json())
            .then((data) => {
              if (data.success) {
                this.$emit("info", "Success", "green");
                this.socket.emit("disconnect_script", {
                  project_name: this.pid,
                  script_name: this.id,
                });
                this.socket.emit("test_delete", {
                  openfaasurl: this.openfaasUrl,
                  project_name: this.pid,
                  script_name: this.id,
                  ids: Object.keys(this.tests),
                });
                this.tests = {};
              } else {
                this.$emit("info", "There was an error deleting tests", "red");
              }
            })
            .catch(function () {
              this.$emit("info", "Could not connect to server", "red");
            });
        }
      );
    },
    start(users, spawnRate, workers, host, time) {
      fetch(this.url, {
        method: "POST",
        body: JSON.stringify({
          command: 5,
          project_name: this.pid,
          script_name: this.id,
          users: parseInt(users),
          spawn_rate: parseInt(spawnRate),
          workers: parseInt(workers),
          host: host,
          time: parseInt(time),
        }),
      })
        .then((data) => data.json())
        .then((data) => {
          if (data.success) {
            const id = data.id;
            const startedAt = data.started_at;
            const info = JSON.stringify({
              users: users,
              spawn_rate: spawnRate,
              host: host,
              workers: workers,
              time: time,
              started_at: startedAt,
            });
            const status = 1;
            const valid = true;
            const test = {
              id: id,
              info: info,
              status: status,
              valid: valid,
              data: JSON.stringify([]),
            };
            // console.log(test);
            this.tests[id] = test;
            // console.log("started: ", test);
            this.registerTest(id);
            this.socket.emit("test_start", {
              openfaasurl: this.openfaasUrl,
              project_name: this.pid,
              script_name: this.id,
              test: test,
            });
          } else {
            this.$emit("info", data.message, "red");
          }
        })
        .catch(() => {
          this.$emit("info", "Could not connect to server", "red");
        });
    },
    startFromModal() {
      if (this.host != null) {
        this.host = this.host.replace("http://", "").replace("https://", "");
        if (this.host != "") {
          this.host = "http://" + this.host;
        }
      }
      // handle false inputs
      if (this.users === "") {
        this.$emit("info", "Users cant be empty", "red");
        return false;
      }
      if (!isInteger(this.users)) {
        this.$emit("info", "Users must be an integer", "red");
        return false;
      }
      if (this.spawnRate === "") {
        this.$emit("info", "Spawn rate cant be empty", "red");
        return false;
      }
      if (!isInteger(this.spawnRate)) {
        this.$emit("info", "Spawn rate must be an integer", "red");
        return false;
      }
      if (this.workers !== "" && !isInteger(this.workers)) {
        this.$emit("info", "workers must be an integer", "red");
        return false;
      }

      if (this.time != "") {
        if (!isInteger(this.time)) {
          this.$emit("info", "Time must be an integer", "red");
          return false;
        }
      }
      this.$refs.dismiss.click();
      if (this.host != "" && this.host != null) {
        localStorage.setItem("last_host", this.host);
      }
      this.start(
        this.users,
        this.spawnRate,
        this.workers,
        this.host,
        this.time
      );
    },
    restart(info) {
      this.start(
        info.users,
        info.spawn_rate,
        info.workers,
        info.host,
        info.time
      );
    },
    deleteTest(id) {
      delete this.tests[id];
      this.socket.emit("test_delete", {
        openfaasurl: this.openfaasUrl,
        project_name: this.pid,
        script_name: this.id,
        ids: [id],
      });
      this.disconnectTest(id);
    },
    stop(id) {
      this.socket.emit("test_stop", {
        openfaasurl: this.openfaasUrl,
        id: id,
      });
    },
  },
  computed: {
    reversedTests() {
      return Object.entries(this.tests).reverse();
    },
  },
  beforeUnmount() {
    this.socket.emit("disconnect_script", {
      project_name: this.pid,
      script_name: this.id,
    });
    this.socket.off(this.openfaasUrl + "_" + this.pid + "_" + this.id);
    this.socket.off(
      this.openfaasUrl + "_" + this.pid + "_" + this.id + "_test_start"
    );
    this.socket.off(
      this.openfaasUrl + "_" + this.pid + "_" + this.id + "_test_delete"
    );

    // console.log("script disconnected");
  },
  mounted() {
    this.init();
  },
  updated() {
    if (this.update) {
      this.init();
      this.$root.updated();
    }
  },
};
</script>

<style>
</style>