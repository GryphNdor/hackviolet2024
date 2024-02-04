// eslint-disable-next-line @typescript-eslint/no-unused-vars
import React from 'react'
import styles from './app.module.css';
import { useTrail, a, useInView } from '@react-spring/web'
import { Parallax, ParallaxLayer, IParallax } from '@react-spring/parallax'
import { useInViewport } from 'react-in-viewport';

const Trail: React.FC<{ open: boolean; children: any }> = ({ open, children }) => {
  const items = React.Children.toArray(children)
  const trail = useTrail(items.length, {
    config: { mass: 5, tension: 2000, friction: 200 },
    opacity: open ? 1 : 0,
    x: open ? 0 : 20,
    height: open ? 110 : 0,
    from: { opacity: 0, x: 20, height: 0 },
  })
  return (
    <div>
      {trail.map(({ height, ...style }, index) => (
        <a.div key={index} className={styles.trailsText} style={style}>
          <a.div style={{ height }}>{items[index]}</a.div>
        </a.div>
      ))}
    </div>
  )
}

export function App() {
  const parallax = React.useRef<IParallax>(null)
  const [ref, inView] = useInView()
  return (
    <>
        <nav>
        <span>check</span>
        <span>check</span>
        <span>check</span>
        </nav>
      <div ref={ref} className={styles.wrapper}>
        <Parallax ref={parallax} pages={3}>
          <ParallaxLayer className={styles.heroContainer}
            offset={0}
            speed={0.1}>
              <div className={styles.container}>
                <Trail open={inView}>
                  <span>Safe</span>
                  <span>Sound</span>
                </Trail>
              <h2>Hear Danger First</h2>
              <button>Try Now</button>
              </div>
            <img className={styles.hero} src="/night.svg"/>
          </ParallaxLayer>

          <ParallaxLayer className={styles.cardContainer}
            offset={1}
            speed={0.4}>

            <h1>HOnk</h1>

            <div>
              <div className={styles.card} style={{backgroundColor:"#EF798A"}}>
                <h1>test</h1>
              </div>
            </div>


          </ParallaxLayer>

          <ParallaxLayer style={{backgroundColor: "lightblue", borderRadius:"50px 50px 0% 0%"}}
            offset={2}
            speed={0.1}>
            <h1>HOnk2</h1>
          </ParallaxLayer>
        </Parallax>
      </div>
    </>
    );
}

export default App;
