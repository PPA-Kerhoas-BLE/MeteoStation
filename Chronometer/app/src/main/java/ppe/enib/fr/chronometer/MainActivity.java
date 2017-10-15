package ppe.enib.fr.chronometer;

import android.net.Uri;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Chronometer;
import android.os.SystemClock;
import android.widget.ListView;
import android.widget.TextView;


import com.google.android.gms.appindexing.Action;
import com.google.android.gms.appindexing.AppIndex;
import com.google.android.gms.common.api.GoogleApiClient;

import java.util.ArrayList;
import java.util.List;
import java.util.logging.Handler;
import java.util.logging.LogRecord;


public class MainActivity extends AppCompatActivity {
    private Button startButton;
    private Button lapButton;
    private Button restartButton;
    private Chronometer chronometer;
    private boolean isRunning;
    private long stopTime;
    private long pauseDuration;

     /* ATTENTION: This was auto-generated to implement the App Indexing API.
     * See https://g.co/AppIndexing/AndroidStudio for more information.
     */
    private GoogleApiClient client;

    //Called after the application launch
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        //Method to find a element in a view
        //This method returns a view and because that its necessary make the cast of a Button
        startButton = (Button) findViewById(R.id.button);
        lapButton = (Button) findViewById(R.id.lapId);
        restartButton = (Button) findViewById(R.id.restartId);
        chronometer = (Chronometer) findViewById(R.id.chrono);
        isRunning = false;



        //chronometer.setFormat(" Time\n(%s)");
        /*O valor apresentado pelo cronometro é calculado pela diferença entre o instante
        actual(SystemClock.elapsedRealtime()) e o valor de referência - aquele que foi "setado"
        através de setBase().
        É por isso que quando volta a chamar start() o cronometro se comporta como não tivesse sido parado.

        Para obter o efeito que pretende tem de ajustar o valor de referência de forma a que a
        diferença entre o instante actual e ele seja igual ao valor apresentado pelo cronometro
        na altura em que foi parado.*/
        startButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

            }
        });
        startButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                if(startButton.getText().equals("Start")){
                    if(!isRunning){
                        chronometer.setBase(SystemClock.elapsedRealtime());
                        chronometer.start();
                        isRunning = true;
                        startButton.setText("Stop");
                    }else{
                        pauseDuration = SystemClock.elapsedRealtime() - stopTime;
                        chronometer.setBase(chronometer.getBase() + pauseDuration);
                        chronometer.start();
                        startButton.setText("Stop");
                    }
                }else if(startButton.getText().equals("Stop")){
                    chronometer.stop();
                    stopTime = SystemClock.elapsedRealtime();
                    startButton.setText("Start");
                }

            }
        });

        restartButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                chronometer.setBase(SystemClock.elapsedRealtime());
                chronometer.stop();
                isRunning = false;
                if(startButton.getText().equals("Stop")){
                    startButton.setText("Start");
                }

            }
        });


        // ATTENTION: This was auto-generated to implement the App Indexing API.
        // See https://g.co/AppIndexing/AndroidStudio for more information.
        client = new GoogleApiClient.Builder(this).addApi(AppIndex.API).build();
    }

    @Override
    public void onStart() {
        super.onStart();

        // ATTENTION: This was auto-generated to implement the App Indexing API.
        // See https://g.co/AppIndexing/AndroidStudio for more information.
        client.connect();
        Action viewAction = Action.newAction(
                Action.TYPE_VIEW, // TODO: choose an action type.
                "Main Page", // TODO: Define a title for the content shown.
                // TODO: If you have web page content that matches this app activity's content,
                // make sure this auto-generated web page URL is correct.
                // Otherwise, set the URL to null.
                Uri.parse("http://host/path"),
                // TODO: Make sure this auto-generated app URL is correct.
                Uri.parse("android-app://ppe.enib.fr.chronometer/http/host/path")
        );
        AppIndex.AppIndexApi.start(client, viewAction);
    }

    @Override
    public void onStop() {
        super.onStop();

        // ATTENTION: This was auto-generated to implement the App Indexing API.
        // See https://g.co/AppIndexing/AndroidStudio for more information.
        Action viewAction = Action.newAction(
                Action.TYPE_VIEW, // TODO: choose an action type.
                "Main Page", // TODO: Define a title for the content shown.
                // TODO: If you have web page content that matches this app activity's content,
                // make sure this auto-generated web page URL is correct.
                // Otherwise, set the URL to null.
                Uri.parse("http://host/path"),
                // TODO: Make sure this auto-generated app URL is correct.
                Uri.parse("android-app://ppe.enib.fr.chronometer/http/host/path")
        );
        AppIndex.AppIndexApi.end(client, viewAction);
        client.disconnect();
    }
}
