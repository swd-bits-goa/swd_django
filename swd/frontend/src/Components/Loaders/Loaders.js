
import React, { PropTypes } from 'react';
import {Card} from 'material-ui/Card';
import ExpandableCard from '../ExpandableCard';
import LinearProgress from 'material-ui/LinearProgress';
import CircularProgress from 'material-ui/CircularProgress';
import ContentLoader, {Facebook, Code, List} from 'react-content-loader'

// Import custom footer styles
import s from './Loaders.css';

const style = {
  center: {
    textAlign: "center",
    padding: "3vw"
  },
};

function CardContentLoader() {
  return (
    <div className={s.container}>
<Card containerStyle={style.center}>
  {/* <LinearProgress mode="indeterminate" /> */}
   {/* <CircularProgress size={60} thickness={7} /> */}
    <ContentLoader
    height={50}
    speed={0.5}
>
    {/* Pure SVG */}
    <rect x="0" y="0" rx="4" ry="4" width="400" height="16"/>
    <rect x="0" y="28" rx="3" ry="3" width="350" height="13"/>
  </ContentLoader>
   
  </Card>
  </div>

  )
}

export {CardContentLoader};