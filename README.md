# a2




              <div class="grid-margin">
                  {% if result %}
                  <div class="card shadow-sm">
                      <div class="card-body">
                          
                          <div class="row ml-1 pt-1 " style="width: fit-content;
                          background: linear-gradient(45deg,rgb(97, 142, 215),#0170a4,#4cacaf);
                          z-index: 999;
                          color: #ffffff;padding-top: 5px;">
                              <h5 style="padding-top: 6px;">Completed Production DA1:</h5>
                              <h5 style="color: rgb(255, 255, 0); font-size: 30px;" class="ml-1 mr-1">{{ l1_count }}</h5>
                          </div>
                          <div class="table-responsive" style="max-height: 50vh;">
                              <table class="table table-striped table-bordered" style="width: 100%;border-collapse: collapse;">
                                  <tbody>
                                      <tr>
                                          <td id="txtwrap">
                                              <div class="row">
                                                  <div class="col-3"><span><b>Id Value:</b> {{result.id_value|nan}} </span></div>
                                                  {% if result.asin %}
                                                  <div class="col-3">
                                                      <span id="asin">
                                                          <b style="color: black;">ASIN:</b>
                                                          {{result.asin|nan}}
                                                      </span>
                                                  </div>
                                                  {% endif %}
                                                  {% if result.product_url %}
                                                  <div class="col-6"><span id="prod_url"
                                                          onclick="window.open('{{result.product_url}}')"><b
                                                              style="color: black;">Product
                                                              Url:</b> {{result.product_url|nan}}</span>
                                                  </div>
                                                  {% endif %}
              
                                              </div>
                                          </td>
                                      </tr>
                                      <tr>
                                          <td id="txtwrap"><b>Question:</b> {{result.question|nan}}</td>
                                      </tr>
                                      <!-- {% if result.asin %} -->
                                      <!-- <tr>
                                          <td id="txtwrap"><b>ASIN:</b> {{result.asin}}</td>
                                      </tr> -->
                                      <!-- {% endif %} -->
                                      {% if result.title %}
                                      <tr>
                                          <td id="txtwrap" class="table-secondary"><b>Product Title:</b> {{result.title|nan}}</td>
                                      </tr>
                                      {% endif %}
                                      <!-- {% if result.product_url %}
                                      <tr>
                                          <td id="txtwrap" class="table-secondary"><b>Product Url:</b><button
                                                  class="btn btn-link btn-sm"
                                                  onclick="window.open('{{result.product_url}}')">{{result.product_url}}</button>
                                          </td>
                                      </tr>
                                      {% endif %} -->
                                      {% if result.imagepath %}
                                      <tr>
                                          <td id="txtwrap" class="table-secondary"><b>Image Url:</b><button
                                                  class="btn btn-link btn-sm"
                                                  onclick="window.open('{{result.imagepath}}')">{{result.imagepath|nan}}</button></td>
                                      </tr>
                                      {% endif %}
                                      {% if result.evidence %}
                                      <tr>
                                          <td id="txtwrap"><b>Evidence:</b> {{result.evidence|nan}}</td>
                                      </tr>
                                      {% endif %}
                                      <tr>
                                          <td id="txtwrap"
                                              style="background-color: #cfffd1 !important;font-size: medium;line-height: 1.5;">
                                              <b>Answer 1: &nbsp;</b>
                                              {{result.answer_one|linebreaks|safe|nan }}
                                          </td>
                                      </tr>
                                      <tr>
                                          <td id="txtwrap"
                                              style="background-color: #ffcdc9 !important;font-size: medium;line-height: 1.5;">
                                              <b>Answer 2: &nbsp;</b>
                                              {{result.answer_two|linebreaks|safe|nan }}
                                          </td>
                                      </tr>
                                  </tbody>
                              </table>
                          </div>
                      </div>
                      <br>
                  </div>
                  <br>
                  <div class="card">
                      <div class="card-body" style="overflow-y: scroll;max-height: 40dvh;">
                          
                          
                          
                      </div>
                  </div>
              
