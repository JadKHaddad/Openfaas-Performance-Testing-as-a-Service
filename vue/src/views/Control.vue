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
      v-for="test in tests"
      :key="test"
      :test="test.info"
      :showPath="true"
      :url="url"
      :openfaasUrl="openfaasUrl"
      :socket="socket"
      :pid="test.project_name"
      :sid="test.script_name"
      :startMinimized="minimizeTests"
      @restart="restart"
      @delete="deleteTest(test)"
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
      tests: [],
      projects: [],
    };
  },
  methods: {
    init() {
      //get running tests
      fetch(this.url, { method: "POST", body: JSON.stringify({ command: 13 }) })
        .then((data) => data.json())
        .then((data) => {
          if (data.success) {
            this.tests = data.tests.reverse();
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
            console.log(data.projects);
            console.log(this.projects);
          }
        })
        .catch(() => {
          this.$emit("info", "Could not connect to server", "red");
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
            const info_ = {
              id: id,
              info: info,
              status: status,
              valid: valid,
              data: JSON.stringify([]),
            };
            const test = {
              id: id,
              info: info_,
              project_name: pid,
              script_name: sid,
            };
            console.log(test);
            this.tests.push(test);
          }
        })
        .catch(() => {
          this.$emit("info", "Could not connect to server", "red");
        });
    },
    deleteTest(test) {
      this.tests = this.tests.filter((t) => t !== test);
    },
    deleteProject(project) {
      this.projects = this.projects.filter((p) => p !== project);
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