<template>
  <div>
    <div class="control-btn-container">
      <button
        type="button"
        class="btn btn-danger btn-block control-btn"
        id="kill-btn"
        @click="killRunningTasks"
      >
        Kill running tasks
      </button>
      <button
        type="button"
        class="btn btn-danger btn-block control-btn"
        id="cleanup-btn"
        @click="deleteAllProjects"
      >
        Delete all projects
      </button>
    </div>
    <InstallationProcess
      v-for="project in projects"
      :key="project"
      :id="project"
      :url="url"
      :openfaasUrl="openfaasUrl"
      :socket="socket"
      @delete="deleteProject(project)"
    >
    </InstallationProcess>

    <Test
      v-for="test in reversedTests"
      :key="test[0]"
      :id="test[0]"
      :info="JSON.parse(test[1].info)"
      :data="JSON.parse(test[1].data)"
      :status="test[1].status"
      :valid="test[1].valid"
      :showPath="true"
      :url="url"
      :openfaasUrl="openfaasUrl"
      :pid="test[1].project_name"
      :sid="test[1].script_name"
      :startMinimized="minimizeTests"
      @restart="restart"
      @delete="deleteTest"
    ></Test>
  </div>
</template>

<script>
import Test from "@/components/Test.vue";
import InstallationProcess from "@/components/InstallationProcess.vue";

export default {
  name: "Control",
  components: {
    Test,
    InstallationProcess,
  },
  props: ["url", "openfaasUrl", "socket", "minimizeTests", "update"],
  data() {
    return {
      tests: {},
      projects: [],
    };
  },
  methods: {
    register() {
      this.socket.off(this.openfaasUrl + "_control");
      this.socket.emit("register_control", { openfaasurl: this.openfaasUrl });
      this.socket.on(this.openfaasUrl + "_control", (msg) => {
        if (IsJsonString(msg)) {
          msg = JSON.parse(msg);
          if (msg.success) {
            for (var key in msg.tests) {
              //console.log(msg.tests[key]);
              const id = msg.tests[key].id;
              if (id in this.tests) {
                this.tests[id].data = msg.tests[key].data;
                this.tests[id].valid = msg.tests[key].valid;
              } else {
                this.tests[id] = msg.tests[key];
              }
            }
          }
        }
      });
      // console.log("control registered")
    },
    init() {
      //get running tests
      fetch(this.url, { method: "POST", body: JSON.stringify({ command: 13 }) })
        .then((data) => data.json())
        .then((data) => {
          if (data.success) {
            this.tests = data.tests;
          }
        })
        .catch(() => {
          this.$emit("info", "Could not connect to server", "red");
        });
      //get installing projects
      fetch(this.url, { method: "POST", body: JSON.stringify({ command: 1 }) })
        .then((data) => data.json())
        .then((data) => {
          if (data.success) {
            this.projects = data.projects;
          }
        })
        .catch(() => {
          this.$emit("info", "Could not connect to server", "red");
        });
      this.register();
      this.socket.on(this.openfaasUrl + "_control_test_delete", (msg) => {
        for (var i = 0; i < msg.length; i++) {
          if (msg[i] in this.tests) {
            delete this.tests[msg[i]];
          }
        }
      });
      this.socket.on(this.openfaasUrl + "_control_test_stop", (msg) => {
        if (msg in this.tests) {
          this.tests[msg].status = 0;
        }
      });
    },
    killRunningTasks() {
      this.$root.setUpConfirmation(
        "Kill all running tasks? Istallation tasks will also be killed",
        "Kill",
        () => {
          fetch(this.url, {
            method: "POST",
            body: JSON.stringify({ command: 911 }),
          })
            .then((data) => data.json())
            .then((data) => {
              if (data.success) {
                this.$emit("info", "Success", "green");
                for (var key in this.tests) {
                  this.tests[key].status = 0;
                }
              } else {
                this.$emit(
                  "info",
                  "There was an error killing running tasks",
                  "red"
                );
              }
            })
            .catch(() => {
              this.$emit("info", "Could not connect to server", "red");
            });
        }
      );
    },
    deleteAllProjects() {
      this.$root.setUpConfirmation("Delete all projects?", "Delete", () => {
        fetch(this.url, {
          method: "POST",
          body: JSON.stringify({ command: 912 }),
        })
          .then((data) => data.json())
          .then((data) => {
            if (data.success) {
              this.$emit("info", "Success", "green");
              this.tests = {};
            } else {
              this.$emit("info", "There was an error deleting projects", "red");
            }
          })
          .catch(() => {
            this.$emit("info", "Could not connect to server", "red");
          });
      });
    },
    restart(info, pid, sid) {
      this.start(
        info.users,
        info.spawn_rate,
        info.workers,
        info.host,
        info.time,
        pid,
        sid
      );
    },
    start(users, spawnRate, workers, host, time, pid, sid) {
      fetch(this.url, {
        method: "POST",
        body: JSON.stringify({
          command: 5,
          project_name: pid,
          script_name: sid,
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
              project_name: pid,
              script_name: sid,
              data: JSON.stringify([]),
            };
            this.tests[id] = test;
            this.socket.emit("test_start", {
              openfaasurl: this.openfaasUrl,
              project_name: pid,
              script_name: sid,
              test: test,
            });
          }
        })
        .catch(() => {
          this.$emit("info", "Could not connect to server", "red");
        });
    },
    deleteTest(id, pid, sid) {
      delete this.tests[id];
      this.socket.emit("test_delete", {
        openfaasurl: this.openfaasUrl,
        project_name: pid,
        script_name: sid,
        ids: [id],
      });
    },
    deleteProject(project) {
      this.projects = this.projects.filter((p) => p !== project);
    },
  },
  computed: {
    reversedTests() {
      return Object.entries(this.tests).reverse();
    },
  },
  beforeUnmount() {
    this.socket.emit("disconnect_control");
    this.socket.off(this.openfaasUrl + "_control");
    this.socket.off(this.openfaasUrl + "_control_test_delete");
    this.socket.off(this.openfaasUrl + "_control_test_stop");
    // console.log("control disconnected")
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