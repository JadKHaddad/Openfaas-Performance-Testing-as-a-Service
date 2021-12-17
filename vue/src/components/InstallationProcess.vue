<template>
  <div class="card project-card" :id="id">
    <div class="card-body">
      <div class="row">
        <div
          class="col-10 project_name"
          data-mdb-toggle="tooltip"
          title="Project name"
        >
          {{ id }}
        </div>
        <div class="col-1">
          <div
            class="spinner-border text-primary spinner"
            data-mdb-toggle="tooltip"
            title="Running"
          ></div>
        </div>
        <div class="col-1" data-mdb-toggle="tooltip" title="Cancel">
          <i class="fas fa-times stop-install-project" @click="stop"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "InstallationProcess",
  props: ["id", "url", "openfaasUrl", "socket"],
  data() {
    return {
      socketIntv: null,
    };
  },
  methods: {
    stop() {
      fetch(this.url, {
        method: "POST",
        body: JSON.stringify({ command: 15, project_name: this.id }),
      })
        .then((data) => data.json())
        .then((data) => {
          if (data.success) {
            this.$root.showInfo(
              this.id + ": installation canceled successfully",
              "green"
            );
            this.$emit("delete");
          } else {
            this.$root.showInfo(
              "There was an error canceling the installation",
              "red"
            );
          }
        })
        .catch(() => {
          this.$root.showInfo("Could not connect to server", "red");
        });
    },
  },
  beforeUnmount() {
    if (this.socketIntv) clearInterval(this.socketIntv);
  },
  mounted() {
    this.socketIntv = setInterval(() => {
      this.socket.emit("task_stats", {
        project_name: this.id,
        openfaasurl: this.openfaasUrl,
      });
    }, 1000);
    this.socket.on(this.id, (msg) => {
      const data = JSON.parse(msg.data);
      if (!data.success) {
        console.log("Something went wrong");
        this.$root.showInfo("Something went wrong", "red");
        clearInterval(this.socketIntv);
      } else if (data.status_code === 3) {
        console.log("thread is locking");
      } else if (data.status_code === 2) {
        console.log("installing project");
      } else if (data.status_code === 1) {
        console.log("installing failed");
        clearInterval(this.socketIntv);
        this.$root.showInfo(
          "Installation failed",
          "red",
          data.error
        );
        this.$emit("delete");
      } else {
        console.log("Task is finished");
        clearInterval(this.socketIntv);
        this.$emit("delete");
        this.$root.showInfo("Installation successs", "green");
      }
    });
  },
};
</script>

<style>
</style>