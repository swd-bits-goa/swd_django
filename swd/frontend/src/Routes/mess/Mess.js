import React from 'react';
import {withApollo} from 'react-apollo';
import {withRouter} from 'react-router-dom';
//import PropTypes from 'prop-types';
import s from './Mess.css'

const messArr=["null","A Mess","C Mess","D Mess"];
const months=["January","February","March","April","May","June","July","August","September","October","November","December","January"];
const now = new Date();
const thisMonth = months[now.getMonth()+1];

class Mess extends React.Component{

  constructor(props) {
    super(props);
    this.state = {radioButton: 0, submitButton: false};

    // This binding is necessary to make `this` work in the callback
    this.handleRadioClick = this.handleRadioClick.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleRadioClick(data) {
    this.setState(state => ({
      radioButton: data
    }));
  }

  handleSubmit(){
    if(this.state.radioButton!=0){
      this.setState(state=>({
        submitButton: true
      }))
    }
  }

  render(){
          return (
            <div className={s.main}>
              {(this.state.radioButton!=0)&&this.state.submitButton?<div className={s.container2}>Congrats! You chose {messArr[this.state.radioButton]} for {thisMonth}</div>:
              <div className={s.allItemsHolder}>
                <div className={s.container1}>
                    <form>
                      <div className={s.headerDiv}>Mess Option</div>
                      <div className={s.radioDiv}>
                        <div className={s.radio1}>
                          <label>
                            <input type="radio" onClick={()=>this.handleRadioClick(1)} checked={this.state.radioButton===1}/>
                            A mess
                          </label>
                        </div>
                        <div className={s.radio2}>
                          <label>
                            <input type="radio" onClick={()=>this.handleRadioClick(2)} checked={this.state.radioButton===2}/>
                            C mess
                          </label>
                        </div>
                        <div className={s.radio3}>
                          <label>
                            <input type="radio" onClick={()=>this.handleRadioClick(3)} checked={this.state.radioButton===3}/>
                            D mess
                          </label>
                        </div>
                      </div>
                    </form>
                </div>
                <button className={s.submitButton} type="submit" onClick={()=>this.handleSubmit()}>Choose</button>
              </div>
              }
            </div>)
  }
}

export default withRouter(withApollo(Mess));


/*<div className={s.container3}>"You've already chosen your mess option"</div>*/
