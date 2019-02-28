<template>
  <div class="container">
    <div class="row has-text-centered">
      <img id="main-image" src="./../assets/profile.png" alt="TheBackyardMoose">
    </div>
    <div class="row has-text-centered">
      <h5 class="subtitle is-5 usage-instructions">Upload a .wav file here.</h5>
      <h5 class="subtitle is-5 usage-instructions">We'll email you the transcript when it's ready!</h5>
    </div>
    <div class="container is-fluid" id="email-container">
      <div class="row has-text-centered">
        <div class="field">
          <div class="control">
            <input
              class="input is-primary"
              type="text"
              id="user-email"
              placeholder="Your email address"
            >
          </div>
        </div>
      </div>
    </div>
    <div class="row has-text-centered">
      <div class="upload-btn-wrapper">
        <button class="button is-link">Upload a file</button>
        <input type="file" name="file" ref="file" v-on:change="handleFileUpload()">
      </div>
    </div>
    <div class="row has-text-centered">
      <a class="button is-primary" v-on:click="submitFile()">Submit</a>
    </div>
    <div class="row has-text-centered"></div>
  </div>
</template>

<style scoped>
#main-image {
  width: 300px;
  height: 280px;
}
.row.has-text-centered {
  padding-top: 15px;
}

.usage-instructions {
  padding: 0px;
  margin-bottom: 8px;
}

.upload-btn-wrapper {
  position: relative;
  overflow: hidden;
  display: inline-block;
}

#email-container {
  width: 300px;
  margin: auto;
}
.upload-btn-wrapper input[type="file"] {
  font-size: 100px;
  position: absolute;
  left: 0;
  top: 0;
  opacity: 0;
}
</style>

<script>
import axios from "axios";
export default {
  /*
      Defines the data used by the component
    */
  data() {
    return {
      file: ""
    };
  },

  methods: {
    /*
        Submits the file to the server
      */
    submitFile() {
      /*
                Initialize the form data
            */
      let formData = new FormData();

      /*
                Add the form data we need to submit
            */
      formData.append("file", this.file);
      var userEmail = document.getElementById("user-email").value;
      formData.append("user-email", userEmail);

      /*
          Make the request to the POST /single-file URL
        */
      axios
        .post("/api/transcribe-audio", formData, {
          headers: { "Content-Type": "multipart/form-data" }
        })
        .then(function() {
          console.log("SUCCESS!!");
        })
        .catch(function() {
          console.log("FAILURE!!");
        });
      this.$emit("toggle-component");
    },

    /*
        Handles a change on the file upload
      */
    handleFileUpload() {
      this.file = this.$refs.file.files[0];
    }
  }
};
</script>