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
        id="delete-script-tests"
        @click="deleteAll"
      >
        Delete all
      </button>
    </div>
    <Test
      v-for="test in tests"
      :key="test"
      :test="test"
      :showPath="false"
      :url="url"
      :openfaasUrl="openfaasUrl"
      :socket="socket"
      :pid="pid"
      :sid="id"
      :startMinimized="minimizeTests"
      @restart="restart"
      @delete="deleteTest(test)"
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
      tests: [],
      users: "",
      spawnRate: "",
      workers: "",
      host: "",
      time: "",
    };
  },
  methods: {
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
            this.tests = data.tests;
            console.log(this.tests[0]);
          }
        })
        .catch(() => {
          this.$emit("info", "Could not connect to server", "red");
        });
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
                this.tests = [];
                this.$emit("info", "Success", "green");
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
            console.log(test);
            this.tests.push(test);
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
      if (this.host != "") {
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
    deleteTest(test) {
      this.tests = this.tests.filter((t) => t !== test);
    },
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