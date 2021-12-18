<template>
  <div>
    <h1 id="message">{{ message }}</h1>
    <div v-if="loading" id="initializing">
      <h4>initializing..</h4>
      <div class="btn-container">
        <div class="spinner-border text-primary spinner"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Openfaas",
  props: ["socket"],
  data() {
    return {
      message: "",
      loading: false,
    };
  },
  mounted() {
    fetch("/openfaas", { method: "POST" })
      .then((data) => data.json())
      .then((data) => {
        //console.log(data);
        this.message = data.message;
        var check = JSON.parse(data.check);
        if (check) {
          this.loading = true;
          this.socket.emit("openfaas");
          this.socket.on("openfaas", (msg) => {
            console.log(msg)
            var message = JSON.parse(msg.data);
            if (message == true) {
              this.message = "function installed";
              this.loading = false;
            }
          });
        }
      })
      .catch(() => {});
  },
  beforeUnmount(){
    this.socket.off("openfaas")
  }
};
</script>

<style>
</style>