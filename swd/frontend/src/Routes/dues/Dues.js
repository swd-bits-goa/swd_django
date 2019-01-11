import React from 'react';
import {withApollo} from 'react-apollo';
import {withRouter} from 'react-router-dom';
import s from './Dues.css';
import arrow from './arrow.svg';

const data=[["Row1","Row1","Row1"],
["Row2","Row2","Row2"],
["Row3","Row3","Row3"],
["Row4","Row4","Row4"],
["Row5","Row5","Row5"],
["Row6","Row6","Row6"],
["Row7","Row7","Row7"],
["Row8","Row8","Row8"],
["Row9","Row9","Row9"]];
const a=0;
class Dues extends React.Component{
  constructor(props) {
    super(props);
    this.state = {details: 0, fees: false};
  }

  handledetailsClick() {
    this.setState(state=> ({
      details :1
    }));
  }
  handlefeesClick() {
    this.setState(state=> ({
      fees :!this.state.fees
    }));
  }

  render(){
    return (
      <div className={s.main}>
      <div className={s.screen}>
      <div className={s.dues}>
      <div className={s.dues_text}>
      Dues
      </div>
      <div className={s.details}>
      Dues details
      <div className={s.imgDiv}><img src={arrow} className={s.img} role="presentation" onClick={()=>this.handledetailsClick()}/></div>
      </div>
      <div className={s.fees} onClick={()=>this.handlefeesClick()}>
      Semester Fees
      <div className={s.imgDiv}><img src={arrow} className={s.img} role="presentation" onClick={()=>this.handledetailsClick()}/></div>
      </div>
      <div className={s.note}>
      Note- (For HD and FD students) mess bill per month is calculated as-<br/><br/>Rs 109 per day:Mess Charges<br/>Rs 22 per day:<br/>Water, Electricity, Security
      </div>
      </div>
      </div>
      {this.state.details===1?
        <div className={s.details_page}>
        <div className={s.dues_text}>
        Dues
        </div>
        <div className={s.dues_head}>Dues Details Sem I</div>
        <div className={s.table}>
        <div className={s.row}>
        <div className={s.first_colHead}>Category</div>
        <div className={s.second_colHead}>Amount</div>
        <div className={s.third_colHead}>Amount</div>
        </div>
        {data.map((items)=>
        <div className={s.row}>
        <div className={s.first_col}>{items[0]}</div>
        <div className={s.second_col}>{items[1]}</div>
        <div className={s.third_col}>{items[2]}</div>
        </div>
      )}
        </div>
        <div className={s.total}>
        <div className={s.total_row}>
        <div className={s.total_col1}>Total Dues</div>
        <div className={s.total_col}>22,500</div>
        </div>
        <div className={s.total_row}>
        <div className={s.total_col1}>Balance</div>
        <div className={s.total_col2}>1,800</div>
        </div>
        </div>
        </div>
      :a=1}
      {this.state.fees===true?
      <div className={s.fees_page}>
      <div className={s.dues_text}>
      Dues
      </div>
      <div className={s.dues_head}>Fee Details Sem I</div>
      <div className={s.table_fees}>
      <div className={s.fees_row}>
      <div className={s.fees_colHead1}>Category</div>
      <div className={s.fees_colHead2}>Amount</div>
      </div>
      <div className={s.fees_row}>
      <div className={s.fees_col1}>Total Fees</div>
      <div className={s.fees_col2}>Rs 191200</div>
      </div>
      <div className={s.fees_row}>
      <div className={s.fees_col1}>After adjusting your fees with previous semester</div>
      <div className={s.fees_col2}>Rs 500</div>
      </div>
      <div className={s.fees_row_last}>
      <div className={s.fees_colHead1}>Total Fees to be paid</div>
      <div className={s.fees_col2}>Rs 191700</div>
      </div>
      <div className={s.back}>
      <button className={s.button} type="submit">Go Back</button>
      </div>
      </div>
      </div>
      :a=2}
      </div>
    )
  }
}

export default withRouter(withApollo(Dues));
