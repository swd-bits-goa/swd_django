
import React, { PropTypes } from 'react';
import {Card} from 'material-ui/Card';
import ExpandableCard from '../ExpandableCard';
import LinearProgress from 'material-ui/LinearProgress';
import CircularProgress from 'material-ui/CircularProgress';

// Import custom footer styles
import s from './Loaders.css';

const style = {
  center: {
    textAlign: "center",
    padding: "3vw"
  },
};

function CardLoader() {
  return (
    <div className={s.container}>
<Card containerStyle={style.center}>
  {/* <LinearProgress mode="indeterminate" /> */}
   <CircularProgress size={60} thickness={7} />
   
  </Card>
  </div>

  )
}

export {CardLoader};