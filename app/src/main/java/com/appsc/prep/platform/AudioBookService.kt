package com.appsc.prep.platform

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.app.ServiceCompat
import androidx.core.content.ContextCompat
import com.appsc.prep.R

/** Keeps "Download today's audiobook" going with the screen off: a notification with its progress and Cancel. */
class AudioBookService : Service() {
    private val main = Handler(Looper.getMainLooper())
    private val tick = object : Runnable {
        override fun run() {
            if (!AudioBook.state.value.active) return
            runCatching { NotificationManagerCompat.from(this@AudioBookService).notify(NOTIFICATION, notification(this@AudioBookService)) }
            main.postDelayed(this, 3000)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        ServiceCompat.startForeground(
            this, NOTIFICATION, notification(this),
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC else 0,
        )
        main.post(tick)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_CANCEL) AudioBook.cancel()
        return START_NOT_STICKY
    }

    override fun onDestroy() {
        main.removeCallbacks(tick)
        super.onDestroy()
    }

    companion object {
        private const val CHANNEL = "audiobook"
        private const val NOTIFICATION = 8
        private const val ACTION_CANCEL = "com.appsc.prep.audiobook.CANCEL"

        fun start(context: Context) {
            runCatching { ContextCompat.startForegroundService(context, Intent(context, AudioBookService::class.java)) }
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, AudioBookService::class.java))
            NotificationManagerCompat.from(context).cancel(NOTIFICATION)
        }

        private fun notification(context: Context): android.app.Notification {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                val nm = context.getSystemService(NotificationManager::class.java)
                if (nm.getNotificationChannel(CHANNEL) == null) {
                    nm.createNotificationChannel(NotificationChannel(CHANNEL, "Audiobook download", NotificationManager.IMPORTANCE_LOW))
                }
            }
            val s = AudioBook.state.value
            val cancel = PendingIntent.getService(
                context, 1, Intent(context, AudioBookService::class.java).setAction(ACTION_CANCEL),
                PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
            )
            return NotificationCompat.Builder(context, CHANNEL)
                .setSmallIcon(R.drawable.ic_stat_listen)
                .setContentTitle("Saving audiobook · ${s.folder}")
                .setContentText("Topic ${(s.done + 1).coerceAtMost(s.total)} of ${s.total}: ${s.current}")
                .setProgress(s.total.coerceAtLeast(1), s.done, false)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .addAction(0, "Cancel", cancel)
                .build()
        }
    }
}
